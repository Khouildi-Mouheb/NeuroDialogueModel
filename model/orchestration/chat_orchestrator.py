from typing import Any, Dict, List, Optional, Tuple

from core.domain.userQuery import UserQuery
from analysis.domain.userState import UserState
from core.context.generatorContext import GeneratorContext
from .config.orchestratorConfig import OrchestratorConfig


class ChatOrchestrator:
    """Orchestrates the end-to-end chat workflow between agents.

    Responsibilities:
    - Control execution flow between analysis agents, generator and verification.
    - Decide dynamically whether to run emotion/intent analysis.
    - Support disabling tools (free mode) via `config`.
    - Retry generation when verification fails (up to `max_retries`).

    Configuration (via `config` dict):
    - enable_emotion: bool (default True)
    - enable_intent: bool (default True)
    - free_mode: bool (default False)
    - max_retries: int (default 1)
    - disabled_tools: List[str] optional list of tool keys to disable

    The class follows single-responsibility and is easily extensible to add
    new analysis agents or verification/utility steps.
    """

    def __init__(
        self,
        generator: Any,
        emotion_agent: Any,
        intent_agent: Any,
        verification_strategy: Any,
        verificators: List[Any],
        config: Optional[Any] = None,
    ):
        self.generator = generator
        self.emotion_agent = emotion_agent
        self.intent_agent = intent_agent
        self.verification_strategy = verification_strategy
        self.verificators = verificators
        # Accept either a dict-like config or an OrchestratorConfig object
        if isinstance(config, OrchestratorConfig):
            cfg = config.to_dict()
        else:
            cfg = (config or {}) if config is not None else {}

        self.config = cfg

        # normalize config with defaults
        self._enable_emotion = bool(self.config.get("enable_emotion", True))
        self._enable_intent = bool(self.config.get("enable_intent", True))
        self._free_mode = bool(self.config.get("free_mode", False))
        self._max_retries = int(self.config.get("max_retries", 1))
        self._disabled_tools = set(self.config.get("disabled_tools", []))

    def orchestrate(self, text: str) -> Dict[str, Any]:
        """High-level orchestration entrypoint.

        Returns a dictionary with keys: `response`, `analysis`, `verification`.
        """
        user_query = UserQuery(text=text)

        # 1. Analysis (may skip based on config or heuristics)
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
                # generator failures should be surfaced but we convert to a verification-style object
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

        # Build response payload similar to previous ChatService output
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
        """Run emotion and intent analysis conditionally.

        Returns a tuple (emotions, intents) where each element may be a
        lightweight sentinel object if skipped to preserve shape.
        """
        # Short-circuit when tools are explicitly disabled in config
        emotions = None
        intents = None

        if self._should_run_emotion(text):
            emotions = self.emotion_agent.detect_emotions(text)
        else:
            emotions = self._empty_emotions()

        if self._should_run_intent(text):
            intents = self.intent_agent.analyze(text)
        else:
            intents = self._empty_intents()

        return emotions, intents

    def _generate(self, context: GeneratorContext) -> str:
        """Generate a response from the generator using the formatted context.

        Honors `disabled_tools` and `free_mode` by refusing to call disabled
        generators.
        """
        if "generator" in self._disabled_tools:
            raise RuntimeError("Generator is disabled by configuration")

        prompt = context.format_context_for_prompt()

        # generator.stream may be an iterator/async generator; join into string
        stream_iter = self.generator.stream(prompt)
        # Defensive: allow generator.stream to return either iterator or string
        if isinstance(stream_iter, str):
            return stream_iter

        return "".join(stream_iter)

    def _verify(self, response: str, text: str, user_state: UserState) -> Any:
        """Run verification and return the verification result object."""
        return self.verification_strategy.execute(
            verificators=self.verificators, response=response, query=text, user_state=user_state
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
        """Default retry handler.

        This method is intentionally small and overridable. Default behavior:
        - If verification provides guidance, append a short clarifying note to
          the user context so the generator will attempt to comply on retry.
        - If verification indicates safety issues, prefer a conservative fallback.

        Returns a (possibly) modified `GeneratorContext`.
        """
        hint = getattr(verification, "hint", None)
        extra_instruction = None

        if hint:
            extra_instruction = f"Verification hint: {hint}. Please update the response accordingly."
        else:
            # Generic conservative instruction for subsequent attempt
            extra_instruction = (
                "The previous response failed verification. Provide a shorter, safer, and more factual reply."
            )

        # create a new context object based on the existing one; contexts are
        # expected to be small wrappers used to build prompts. We append an
        # instruction onto the user_query text for the generator to use.
        new_user_query = UserQuery(text=(user_query.text + "\n\n" + extra_instruction))

        return self._build_context(user_query=new_user_query, user_state=user_state)

    def _build_context(self, user_query: UserQuery, user_state: UserState) -> GeneratorContext:
        """Construct the `GeneratorContext` from user query and state."""
        return GeneratorContext(user_query=user_query, user_state=user_state)

    def _should_run_emotion(self, text: str) -> bool:
        """Decide whether to run emotion analysis.

        Rules:
        - Disabled if global flag off or tool listed in `disabled_tools` or in `free_mode`.
        - Basic heuristic: skip short, single-word messages.
        """
        if not self._enable_emotion:
            return False
        if self._free_mode or "emotion_agent" in self._disabled_tools:
            return False
        if not text or len(text.strip().split()) <= 1:
            return False
        return True

    def _should_run_intent(self, text: str) -> bool:
        """Decide whether to run intent analysis.

        Similar rules to `_should_run_emotion` but may be enabled for shorter text.
        """
        if not self._enable_intent:
            return False
        if self._free_mode or "intent_agent" in self._disabled_tools:
            return False
        # intents can be useful even for short messages
        return bool(text and text.strip())

    # Helpers for empty analysis placeholders
    def _empty_emotions(self):
        class _Empty:
            emotions = None
            emotionsWithScore = None

        return _Empty()

    def _empty_intents(self):
        class _Empty:
            result = None

        return _Empty()

    def _make_failure_verification(self, message: str):
        """Create a minimal verification-like object when generation fails."""
        class _V:
            is_approved = False
            fallback_response = f"Generation failed: {message}"
            overall_score = 0.0
            issues = []

        return _V()
