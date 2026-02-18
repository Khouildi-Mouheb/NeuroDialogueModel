"""
ChatOrchestrator - Application layer orchestrator for chat workflow.

Dependencies: Ports only (no adapters).
Orchestrates: emotion detection, intent analysis, generation, and verification.
"""
from typing import Any, Dict, List, Optional, Tuple
from domain.entities.user_query import UserQuery
from domain.value_objects.user_state import UserState
from domain.context.generator_context import GeneratorContext


class ChatOrchestrator:
    """Orchestrates the end-to-end chat workflow using port-based dependencies.
    
    Responsibilities:
    - Control execution flow between analysis agents, generator and verification.
    - Decide dynamically whether to run emotion/intent analysis.
    - Support disabling tools (free mode) via config.
    - Retry generation when verification fails.
    
    Dependencies: Ports only (no direct adapter imports).
    """

    def __init__(
        self,
        llm_port: Any,  # LLMPort
        emotion_port: Any,  # EmotionPort
        intent_port: Any,  # IntentPort
        verification_strategy_port: Any,  # VerificationStrategyPort
        verificators: List[Any],  # List[VerificationPort]
        config: Optional[Dict] = None,
    ):
        self.llm_port = llm_port
        self.emotion_port = emotion_port
        self.intent_port = intent_port
        self.verification_strategy_port = verification_strategy_port
        self.verificators = verificators
        
        # Handle config
        cfg = (config or {}) if config is not None else {}
        self.config = cfg
        
        # normalize config with defaults
        self._enable_emotion = bool(self.config.get("enable_emotion", True))
        self._enable_intent = bool(self.config.get("enable_intent", True))
        self._free_mode = bool(self.config.get("free_mode", False))
        self._max_retries = int(self.config.get("max_retries", 1))
        self._disabled_tools = set(self.config.get("disabled_tools", []))

    def orchestrate(self, text: str) -> Dict[str, Any]:
        """High-level orchestration entrypoint."""
        user_query = UserQuery(text=text)

        # 1. Analysis (may skip based on config)
        emotions, intents = self._analyze(text)

        # 2. Build user state and context
        user_state = UserState(emotions=emotions, intentsAndNeeds=intents)
        context = self._build_context(user_query=user_query, user_state=user_state)

        # 3. Generate + verify with retry support
        attempt = 0
        final_response = None
        final_verification = None
        last_generated = ""

        while attempt <= self._max_retries:
            attempt += 1
            try:
                last_generated = self._generate(context)
            except Exception as e:
                final_verification = self._make_failure_verification(str(e))
                break

            final_verification = self._verify(last_generated, text, user_state)

            if final_verification.is_approved:
                final_response = last_generated
                break

            # If verification failed and we can retry, allow handler to modify context
            if attempt <= self._max_retries:
                context = self._handle_retry(
                    attempt=attempt,
                    response=last_generated,
                    verification=final_verification,
                    context=context,
                    user_query=user_query,
                    user_state=user_state,
                )
            else:
                # final fallback
                final_response = final_verification.fallback_response or last_generated

        # Build response payload
        payload = {
            "response": final_response or last_generated,
            "analysis": {
                "emotions": getattr(emotions, "emotions", None),
                "emotion_scores": getattr(emotions, "emotionsWithScore", None),
                "intents": getattr(intents, "result", None),
            },
            "verification": {
                "approved": bool(getattr(final_verification, "is_approved", False)),
                "score": getattr(final_verification, "overall_score", None),
                "issues": [i.value for i in getattr(final_verification, "issues", [])]
                if getattr(final_verification, "issues", None)
                else [],
            },
        }

        return payload

    def _analyze(self, text: str) -> Tuple[Any, Any]:
        """Run emotion and intent analysis conditionally."""
        emotions = None
        intents = None

        if self._should_run_emotion(text):
            emotions = self.emotion_port.detect_emotions(text)
        else:
            emotions = self._empty_emotions()

        if self._should_run_intent(text):
            intents = self.intent_port.analyze(text)
        else:
            intents = self._empty_intents()

        return emotions, intents

    def _generate(self, context: GeneratorContext) -> str:
        """Generate a response from the LLM port."""
        if "generator" in self._disabled_tools:
            raise RuntimeError("Generator is disabled by configuration")

        prompt = context.format_context_for_prompt()
        stream_iter = self.llm_port.stream(prompt)
        
        # Defensive: allow LLM to return either iterator or string
        if isinstance(stream_iter, str):
            return stream_iter

        return "".join(stream_iter)

    def _verify(self, response: str, text: str, user_state: UserState) -> Any:
        """Run verification and return the result object."""
        return self.verification_strategy_port.execute(
            verificators=self.verificators,
            response=response,
            query=text,
            user_state=user_state
        )

    def _build_context(self, user_query: UserQuery, user_state: UserState) -> GeneratorContext:
        """Build generator context from query and state."""
        return GeneratorContext(
            user_query=user_query,
            user_state=user_state
        )

    def _handle_retry(
        self,
        attempt: int,
        response: str,
        verification: Any,
        context: GeneratorContext,
        user_query: UserQuery,
        user_state: UserState,
    ) -> GeneratorContext:
        """Default retry handler - provide guidance to generator for next attempt."""
        hint = getattr(verification, "hint", None)
        extra_instruction = None

        if hint:
            extra_instruction = f"Verification hint: {hint}. Please update the response accordingly."
        else:
            extra_instruction = (
                "The previous response failed verification. Provide a shorter, safer, and more factual reply."
            )

        # For now, return unchanged context (could be enhanced to modify prompt)
        return context

    def _should_run_emotion(self, text: str) -> bool:
        """Check if emotion analysis should run."""
        if not self._enable_emotion or "emotion" in self._disabled_tools:
            return False
        return True

    def _should_run_intent(self, text: str) -> bool:
        """Check if intent analysis should run."""
        if not self._enable_intent or "intent" in self._disabled_tools:
            return False
        return True

    def _empty_emotions(self):
        """Return empty emotions sentinel."""
        from domain.value_objects.emotion_result import EmotionResult
        return EmotionResult()

    def _empty_intents(self):
        """Return empty intents sentinel."""
        from domain.value_objects.intent_and_needs_result import IntentAndNeedsResult
        return IntentAndNeedsResult()

    def _make_failure_verification(self, error_msg: str):
        """Create a failure verification result."""
        from adapters.verification.verification_models import VerificationResult, VerificationStatus
        return VerificationResult(
            is_approved=False,
            status=VerificationStatus.REJECTED,
            scores={},
            issues=[],
            fallback_response=f"[ERROR] {error_msg}"
        )
