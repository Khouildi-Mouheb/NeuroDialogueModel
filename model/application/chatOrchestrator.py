from typing import Optional, List, Any, Dict


class ChatOrchestrator:
    """Dependency-injected orchestrator for the full chat workflow.

    This class intentionally avoids importing project modules at top-level
    (some project modules have fragile imports). Instead it accepts
    ready-to-use component instances (duck-typed):

    - embedding_model: has `embedText(text)` or `embedtext(text)`
    - retriever: has `retrieve(query, top_k)` returning list of results
    - generator: has `stream(prompt)` (yields) or `generate(prompt)` (returns str)
    - analysis_agents: list of agents (emotion, intent) with methods like
      `detect_emotions(text)` and `analyze(text)`
    - verifiers: list of verifier agents with `verify(reply, user_state)`
    - indexer: optional document indexer

    All calls are defensive (check for attribute existence) so this
    orchestrator can be used even when some components are missing.
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
            # Emotion agent
            if hasattr(agent, "detect_emotions"):
                try:
                    emotions = agent.detect_emotions(text)
                    user_state["emotions"] = emotions
                except Exception:
                    user_state.setdefault("emotions", None)

            # Intent / needs agent
            if hasattr(agent, "analyze"):
                try:
                    intent_result = agent.analyze(text)
                    user_state["intentsAndNeeds"] = intent_result
                    # keep convenience fields if present
                    if hasattr(intent_result, "result"):
                        user_state["intents"] = intent_result.result.get("intents")
                        user_state["needs"] = intent_result.result.get("needs")
                except Exception:
                    user_state.setdefault("intentsAndNeeds", None)

        return user_state

    def _embedQuery(self, query: str):
        if not self.embedding_model:
            return None

        # prefer camelCase `embedText`, fallback to `embedtext`
        if hasattr(self.embedding_model, "embedText"):
            return self.embedding_model.embedText(query)
        if hasattr(self.embedding_model, "embedtext"):
            return self.embedding_model.embedtext(query)
        if hasattr(self.embedding_model, "embedBatch"):
            return self.embedding_model.embedBatch([query])[0]
        return None

    def _retrieve(self, query: str, query_vector: Any = None, top_k: int = 5) -> List[Dict[str, Any]]:
        # Prefer a retriever interface
        if self.retriever and hasattr(self.retriever, "retrieve"):
            try:
                return self.retriever.retrieve(query, top_k=top_k)
            except Exception:
                pass

        # If retriever missing but a vector store-like object provided
        if self.retriever and hasattr(self.retriever, "query_vectors") and query_vector is not None:
            try:
                return self.retriever.query_vectors(query_vector=query_vector, top_k=top_k)
            except Exception:
                pass

        return []

    def _formatPrompt(self, query: str, retrieved: List[Dict[str, Any]], user_state: Dict[str, Any]) -> str:
        parts = ["Answer concisely using retrieved documents when relevant."]
        parts.append(f"User Query: {query}")

        if user_state:
            parts.append(f"User State: {user_state}")

        if retrieved:
            parts.append("Retrieved Information:")
            for i, r in enumerate(retrieved, 1):
                text = r.get("text") or r.get("metadata", {}).get("text") or r.get("chunk_text") or ""
                parts.append(f"Chunk {i}: {text}")

        return "\n\n".join(parts)

    def _generateReply(self, prompt: str) -> str:
        if not self.generator:
            return "[NO GENERATOR CONFIGURED]"

        # If generator supports streaming
        if hasattr(self.generator, "stream"):
            try:
                pieces = []
                for chunk in self.generator.stream(prompt):
                    pieces.append(chunk)
                return "".join(pieces)
            except Exception:
                # fallback to sync generate if available
                pass

        if hasattr(self.generator, "generate"):
            try:
                return self.generator.generate(prompt)
            except Exception:
                return "[GENERATION ERROR]"

        # Last resort: call __call__
        try:
            return str(self.generator(prompt))
        except Exception:
            return "[GENERATOR NOT CALLABLE]"

    def _verifyReply(self, reply: str, user_state: Dict[str, Any]) -> str:
        # Run verifiers sequentially; they may return modified reply or raise
        for verifier in self.verifiers:
            try:
                if hasattr(verifier, "verify"):
                    result = verifier.verify(reply, user_state)
                    if isinstance(result, str):
                        reply = result
                elif hasattr(verifier, "assess"):
                    res = verifier.assess(reply, user_state)
                    if isinstance(res, dict) and res.get("modified"):
                        reply = res.get("reply", reply)
            except Exception:
                continue
        return reply

    def handleUserMessage(self, user_message: str, user_id: Optional[str] = None, top_k: int = 5) -> str:
        """Run the end-to-end flow and return assistant reply.

        Steps:
        1. Run analysis agents to build a lightweight user state
        2. Embed query (if embedding model available)
        3. Retrieve candidate chunks
        4. Build a prompt from query, retrieved results and user state
        5. Generate reply (stream or sync)
        6. Run verifiers and return final reply
        """
        # 1. Analysis
        user_state = self._runAnalysis(user_message)

        # 2. Embed
        query_vector = self._embedQuery(user_message)

        # 3. Retrieve
        retrieved = self._retrieve(user_message, query_vector=query_vector, top_k=top_k)

        # 4. Prompt
        prompt = self._formatPrompt(user_message, retrieved, user_state)

        # 5. Generate
        reply = self._generateReply(prompt)

        # 6. Verify
        final_reply = self._verifyReply(reply, user_state)

        return final_reply
