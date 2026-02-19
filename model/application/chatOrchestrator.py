from typing import Optional, List, Any, Dict

from domain.valueObjects.aggregatedVerificationResult import AggregatedVerificationResult
from domain.valueObjects.empathyVerificationResult import EmpathyVerificationResult
from domain.valueObjects.appropriatenessVerificationResult import AppropriatenessVerificationResult
from domain.valueObjects.safetyVerificationResult import SafetyVerificationResult
from domain.enums.verificationStatus import VerificationStatus


class ChatOrchestrator:
    """Dependency-injected orchestrator for the full chat workflow.

    Accepts ready-to-use component instances (duck-typed):

    - embedding_model : has `embedText(text)`
    - retriever       : has `retrieve(query, top_k)`
    - generator       : has `stream(prompt)` (yields) or `generate(prompt)` → str
    - analysis_agents : list — emotion agent (`detect_emotions`) + intent agent (`analyze`)
    - verifiers       : exactly three verifier agents in order:
                          [EmpathyVerificator, AppropriatenessVerificator, SafetyVerificator]
    - indexer         : optional document indexer
    """

    def __init__(
        self,
        embedding_model: Any = None,
        retriever: Any = None,
        generator: Any = None,
        analysis_agents: Optional[List[Any]] = None,
        verifiers: Optional[List[Any]] = None,
        indexer: Any = None,
    ) -> None:
        self.embedding_model = embedding_model
        self.retriever = retriever
        self.generator = generator
        self.analysis_agents = analysis_agents or []
        self.verifiers = verifiers or []
        self.indexer = indexer



    def _runAnalysis(self, text: str) -> Dict[str, Any]:
        user_state: Dict[str, Any] = {}

        for agent in self.analysis_agents:
            if hasattr(agent, "detect_emotions"):
                try:
                    user_state["emotions"] = agent.detect_emotions(text)
                except Exception:
                    user_state.setdefault("emotions", None)

            if hasattr(agent, "analyze"):
                try:
                    intent_result = agent.analyze(text)
                    user_state["intentsAndNeeds"] = intent_result
                    if hasattr(intent_result, "result"):
                        user_state["intents"] = intent_result.result.get("intents")
                        user_state["needs"] = intent_result.result.get("needs")
                except Exception:
                    user_state.setdefault("intentsAndNeeds", None)
        return user_state

    def _embedQuery(self, query: str) -> Any:
        if not self.embedding_model:
            return None
        if hasattr(self.embedding_model, "embedText"):
            return self.embedding_model.embedText(query)
        if hasattr(self.embedding_model, "embedtext"):
            return self.embedding_model.embedtext(query)
        if hasattr(self.embedding_model, "embedBatch"):
            return self.embedding_model.embedBatch([query])[0]
        return None

    def _retrieve(
        self, query: str, query_vector: Any = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if self.retriever and hasattr(self.retriever, "retrieve"):
            try:
                return self.retriever.retrieve(query, top_k=top_k)
            except Exception:
                pass

        if self.retriever and hasattr(self.retriever, "query_vectors") and query_vector is not None:
            try:
                return self.retriever.query_vectors(query_vector=query_vector, top_k=top_k)
            except Exception:
                pass

        return []

    def _formatPrompt(
        self, query: str, retrieved: List[Dict[str, Any]], user_state: Dict[str, Any]
    ) -> str:
        parts = ["Answer concisely using retrieved documents when relevant."]
        parts.append(f"User Query: {query}")

        if user_state:
            parts.append(f"User State: {user_state}")

        if retrieved:
            parts.append("Retrieved Information:")
            for i, r in enumerate(retrieved, 1):
                text = (
                    r.get("text")
                    or r.get("metadata", {}).get("text")
                    or r.get("chunk_text")
                    or ""
                )
                parts.append(f"Chunk {i}: {text}")

        return "\n\n".join(parts)

    def _generateReply(self, prompt: str) -> str:
        if not self.generator:
            return "[NO GENERATOR CONFIGURED]"

        if hasattr(self.generator, "stream"):
            try:
                return "".join(chunk for chunk in self.generator.stream(prompt))
            except Exception:
                pass

        if hasattr(self.generator, "generate"):
            try:
                return self.generator.generate(prompt)
            except Exception:
                return "[GENERATION ERROR]"

        try:
            return str(self.generator(prompt))
        except Exception:
            return "[GENERATOR NOT CALLABLE]"

    def _verifyReply(
        self, reply: str, user_state: Dict[str, Any]
    ) -> tuple[str, AggregatedVerificationResult | None]:
        """Run the three typed verifiers and return (final_reply, aggregated_result).

        Verification flow
        -----------------
        1. Run each verifier in order: Empathy → Appropriateness → Safety.
        2. Wrap the three typed results in AggregatedVerificationResult.
        3. If overall status is REJECTED → return the fallback response immediately.
        4. If overall status is NEEDS_REVISION → return the original reply anyway
           (the orchestrator logs recommendations but does not block the response;
           callers that want to act on them can inspect the returned result).
        5. If APPROVED → return reply unchanged.

        Returns a tuple so callers can optionally inspect the full aggregated result.
        """
        if len(self.verifiers) < 3:
            # Not enough verifiers configured — skip verification entirely
            return reply, None

        empathy_verificator, appropriateness_verificator, safety_verificator = (
            self.verifiers[0],
            self.verifiers[1],
            self.verifiers[2],
        )

        # --- Run each verifier ---
        empathy_result: EmpathyVerificationResult = empathy_verificator.verify(
            reply, user_state=user_state
        )
        appropriateness_result: AppropriatenessVerificationResult = (
            appropriateness_verificator.verify(reply, user_state=user_state)
        )
        safety_result: SafetyVerificationResult = safety_verificator.verify(
            reply, user_state=user_state
        )

        # --- Aggregate ---
        aggregated = AggregatedVerificationResult(
            empathy=empathy_result,
            appropriateness=appropriateness_result,
            safety=safety_result,
        )

        # --- Act on overall verdict ---
        if aggregated.status == VerificationStatus.REJECTED:
            # Safety hard-blocked the reply — use the fallback
            final_reply = aggregated.fallback_response or (
                "I'm sorry, I need to rephrase that. Could you give me a moment?"
            )
            return final_reply, aggregated

        if aggregated.status == VerificationStatus.NEEDS_REVISION:
            # Soft issues — pass the reply through but surface recommendations
            # so the caller / logging layer can act on them
            return reply, aggregated

        # APPROVED — all good
        return reply, aggregated

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handleUserMessage(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> str:
        """Run the end-to-end flow and return the assistant reply.

        Steps
        -----
        1. Analyse   — build user state (emotions, intents, needs)
        2. Embed     — vectorise the query
        3. Retrieve  — fetch relevant chunks
        4. Prompt    — assemble prompt from query + context + user state
        5. Generate  — produce a reply (streaming or sync)
        6. Verify    — run Empathy / Appropriateness / Safety verificators
        """
        user_state  = self._runAnalysis(user_message)
        query_vector = self._embedQuery(user_message)
        retrieved   = self._retrieve(user_message, query_vector=query_vector, top_k=top_k)
        prompt      = self._formatPrompt(user_message, retrieved, user_state)
        reply       = self._generateReply(prompt)

        final_reply, aggregated = self._verifyReply(reply, user_state)

        return final_reply

    def handleUserMessageWithVerification(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> tuple[str, AggregatedVerificationResult | None]:
        """Same as handleUserMessage but also returns the full AggregatedVerificationResult.

        Useful for callers that want to log issues, surface recommendations to
        a developer dashboard, or trigger a retry loop on NEEDS_REVISION.
        """
        user_state   = self._runAnalysis(user_message)
        query_vector = self._embedQuery(user_message)
        retrieved    = self._retrieve(user_message, query_vector=query_vector, top_k=top_k)
        prompt       = self._formatPrompt(user_message, retrieved, user_state)
        reply        = self._generateReply(prompt)

        final_reply, aggregated = self._verifyReply(reply, user_state)

        return final_reply, aggregated


