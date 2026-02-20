from typing import Optional, Tuple
from domain.services.userState import UserState
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.orchestrationState import OrchestrationState
from domain.valueObjects.aggregatedVerificationResult import AggregatedVerificationResult
from domain.context.generatorContext import GeneratorContext
from domain.entities.query.userQuery import UserQuery
from application.config.systemComponents import SystemComponents


class ChatOrchestrator:
    """End-to-end orchestrator for the chat pipeline.

    Pipeline
    --------
    1. ANALYZING   — detect emotions, intents, needs → UserState
    2. EMBEDDING   — embed the user query
    3. RETRIEVING  — fetch relevant chunks from vector store
    4. PROMPTING   — assemble GeneratorContext
    5. GENERATING  — stream or generate full response
    6. VERIFYING   — run Empathy / Appropriateness / Safety verificators
    """

    def __init__(self, components: SystemComponents) -> None:
        self.components = components
        self.state = OrchestrationState.IDLE

    # ------------------------------------------------------------------ #
    # Pipeline steps                                                       #
    # ------------------------------------------------------------------ #

    def _analyze(self, user_message: str) -> UserState:
        self.state = OrchestrationState.ANALYZING
        user_state = UserState()

        for agent in self.components.analysis_agents:
            if hasattr(agent, "detectEmotions"):
                user_state.emotions = agent.detectEmotions(user_message)

            if hasattr(agent, "analyze"):
                result = agent.analyze(user_message)
                user_state.intentsAndNeeds = result

        return user_state

    def _embed(self, user_message: str):
        self.state = OrchestrationState.EMBEDDING
        return self.components.embedding_model.embedText(user_message)

    def _retrieve(self, user_message: str, top_k: int = 5):
        self.state = OrchestrationState.RETRIEVING
        return self.components.retriever.retrieve(user_message, top_k=top_k)

    def _buildContext(
        self,
        user_message: str,
        retrieved: list,
        user_state: UserState,
    ) -> GeneratorContext:
        self.state = OrchestrationState.PROMPTING
        user_query = UserQuery(text=user_message)
        return GeneratorContext(
            user_query=user_query,
            retrieved_chunks=retrieved,
            user_state=user_state,
        )

    def _generate(self, context: GeneratorContext) -> str:
        self.state = OrchestrationState.GENERATING
        return self.components.generator.generateFullResponse(context)

    def _verify(
        self,
        reply: str,
        user_state: UserState,
    ) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        self.state = OrchestrationState.VERIFYING

        if len(self.components.verifiers) < 3:
            return reply, None

        empathy_result         = self.components.verifiers[0].verify(reply, user_state=user_state)
        appropriateness_result = self.components.verifiers[1].verify(reply, user_state=user_state)
        safety_result          = self.components.verifiers[2].verify(reply, user_state=user_state)

        aggregated = AggregatedVerificationResult(
            empathy=empathy_result,
            appropriateness=appropriateness_result,
            safety=safety_result,
        )

        if aggregated.status == VerificationStatus.REJECTED:
            fallback = aggregated.fallback_response or (
                "I'm sorry, I need to rephrase that. Could you give me a moment?"
            )
            return fallback, aggregated

        return reply, aggregated

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def handleUserMessage(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> str:
        user_state  = self._analyze(user_message)
        _           = self._embed(user_message)
        retrieved   = self._retrieve(user_message, top_k=top_k)
        context     = self._buildContext(user_message, retrieved, user_state)
        reply       = self._generate(context)
        final_reply, _ = self._verify(reply, user_state)

        self.state = OrchestrationState.COMPLETED
        return final_reply

    def handleUserMessageWithVerification(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        user_state  = self._analyze(user_message)
        _           = self._embed(user_message)
        retrieved   = self._retrieve(user_message, top_k=top_k)
        context     = self._buildContext(user_message, retrieved, user_state)
        reply       = self._generate(context)
        final_reply, aggregated = self._verify(reply, user_state)

        self.state = OrchestrationState.COMPLETED
        return final_reply, aggregated