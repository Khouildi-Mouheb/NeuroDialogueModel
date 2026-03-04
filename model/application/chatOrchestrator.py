from typing import Optional, Tuple
from domain.services.userState import UserState
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.orchestrationState import OrchestrationState
from domain.valueObjects.aggregatedVerificationResult import AggregatedVerificationResult
from domain.context.generatorContext import GeneratorContext
from domain.entities.query.userQuery import UserQuery
from application.config.systemComponents import SystemComponents


class ChatOrchestrator:


    def __init__(self, components: SystemComponents) -> None:
        self.components = components
        self.state = OrchestrationState.IDLE



    def _analyze(self, user_message: str) -> UserState:
        self.state = OrchestrationState.ANALYZING
        user_state = UserState()

        for agent in self.components.analysis_agents:
            if hasattr(agent, "detectEmotions"):
                user_state.emotions = agent.detectEmotions(user_message)

            if hasattr(agent, "analyze"):
                result = agent.analyze(user_message)
                user_state.intentsAndNeeds = result
                user_state.intents = result.result['intents']
                user_state.needs = result.result['needs']
        return user_state
    
    def _classifyQuery(self, user_message: str) -> Optional[str]:
        for agent in self.components.analysis_agents:
            if hasattr(agent, "classifyQuery"):
                category = agent.classifyQuery(user_message)
                return category
        return None
    
    def _embed(self, user_message: str):
        self.state = OrchestrationState.EMBEDDING
        return self.components.embedding_model.embedText(user_message)

    def _retrieve(self, user_message: str, 
                  top_k: int = 5,
                  queryType: Optional[str] = None) -> list:
        self.state = OrchestrationState.RETRIEVING
        return self.components.retriever.retrieve(user_message, top_k=top_k, queryType=queryType)

    def _buildGeneratorContext(
        self,
        user_message: str,
        retrieved: list = None,
        user_state: UserState = None,
        queryType: Optional[str] = None,

    ) -> GeneratorContext:
        self.state = OrchestrationState.PROMPTING
        user_query = UserQuery(
            text=user_message,
            queryType=queryType)
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
        user_state: UserState = None,
    ) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        self.state = OrchestrationState.VERIFYING

        if len(self.components.verifiers) < 3:
            return reply, None

        empathy_result         = self.components.verifiers[0].verify(reply, user_state=user_state)
        print(f"the empathy result is : {empathy_result}")
        appropriateness_result = self.components.verifiers[1].verify(reply, user_state=user_state)
        print(f"the appropriateness result is : {appropriateness_result}")
        safety_result          = self.components.verifiers[2].verify(reply, user_state=user_state)
        print(f"the safety result is : {safety_result}")

        
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



    def handleUserMessage(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> str:
        print("Handling user message through orchestrator...")
        queryType   = self._classifyQuery(user_message)
        if queryType == 'greetings_and_bye':
            reply = self.components.generator.generateSimpleResponse(user_message, queryType=queryType)
            final_reply, aggregated = self._verify(reply, user_state)
            return final_reply, aggregated
        
        user_state  = self._analyze(user_message)
        _           = self._embed(user_message )
        retrieved   = self._retrieve(user_message, top_k=top_k , queryType=queryType)
        context     = self._buildGeneratorContext(user_message, retrieved, user_state , queryType=queryType)
        reply       = self._generate(context)
        
        return reply, None

    def handleUserMessageWithVerification(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        print("Handling user message with verification through orchestrator...")
        queryType   = self._classifyQuery(user_message)


        if queryType == 'greetings_and_bye':
            reply = self.components.generator.generateSimpleResponse(user_message, queryType=queryType)
            final_reply, aggregated = self._verify(reply)
            return final_reply, None
        
        user_state  = self._analyze(user_message)
        _           = self._embed(user_message)
        retrieved   = self._retrieve(user_message, top_k=top_k , queryType=queryType)
        print(f"the retrieved docs are : {retrieved}")
        context     = self._buildGeneratorContext(user_message, retrieved, user_state , queryType=queryType)
        print(f"the context for generation is : {context.format_context_for_prompt()}")
        reply       = self._generate(context)
        final_reply, aggregated = self._verify(reply, user_state)

        self.state = OrchestrationState.COMPLETED
        return final_reply, aggregated