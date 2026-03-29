import json
from typing import Optional, Tuple, List
from domain.services.userState import UserState
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.orchestrationState import OrchestrationState
from domain.valueObjects.aggregatedVerificationResult import AggregatedVerificationResult
from domain.context.generatorContext import GeneratorContext
from domain.context.summaryContext import SummaryContext
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
                return agent.classifyQuery(user_message)
        return None

    def _embed(self, user_message: str):
        self.state = OrchestrationState.EMBEDDING
        return self.components.embedding_model.embedText(user_message)

    def _retrieve(self, user_message: str,
                  top_k: int = 5,
                  queryType: Optional[str] = None) -> list:
        self.state = OrchestrationState.RETRIEVING
        return self.components.retriever.retrieve(user_message,
                                                  top_k=top_k,
                                                  queryType=queryType)

    def _buildGeneratorContext(
        self,
        user_message: str,
        retrieved: list = None,
        user_state: UserState = None,
        queryType: Optional[str] = None,
        history: Optional[List[dict]] = None,
        summary: Optional[str] = None,
        user_profile: Optional[str] = None,
    ) -> GeneratorContext:
        self.state = OrchestrationState.PROMPTING
        user_query = UserQuery(
            text=user_message,
            queryType=queryType)
        return GeneratorContext(
            user_query=user_query,
            retrieved_chunks=retrieved,
            user_state=user_state,
            history=history,
            summary=summary,
            user_profile=user_profile,
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

    def _summarize(
        self,
        user_id: str,
        chat_id: str,
        history: List[dict],
    ) -> None:
        existing_summary = self.components.memoryAdapter.getSummary(user_id, chat_id)
        existing_profile = self.components.memoryAdapter.getProfile(user_id, chat_id)
        
        # Combine summary and profile for context if needed
        combined_context = f"{existing_summary}\n{existing_profile}" if existing_profile else existing_summary

        summary_context = SummaryContext(
            history=history,
            existing_summary=combined_context
        )
        new_memory_raw = self.components.generator.generateSimpleResponse(
            summary_context.format_context_for_prompt()
        )

        # Basic parsing of the LLM output based on the sections defined in SummaryContext
        parts = new_memory_raw.split("Section 2:")
        summary_text = parts[0].replace("Section 1:", "").strip()
        profile_text = parts[1].strip() if len(parts) > 1 else ""

        self.components.memoryAdapter.updateMemory(user_id, chat_id, summary_text, profile_text)

    def handleUserMessage(
        self,
        user_message: str,
        top_k: int = 5,
    ) -> Tuple[str, None]:
        print("Handling user message through orchestrator...")
        queryType = self._classifyQuery(user_message)

        if queryType == 'greetings_and_bye':
            reply = self.components.generator.generateSimpleResponse(user_message, queryType=queryType)
            return reply, None

        user_state = self._analyze(user_message)
        _          = self._embed(user_message)
        retrieved  = self._retrieve(user_message, top_k=top_k, queryType=queryType)
        context    = self._buildGeneratorContext(user_message, retrieved, user_state, queryType=queryType)
        reply      = self._generate(context)

        return reply, None

    def handleUserMessageWithVerification(
        self,
        user_message: str,
        user_id: str,
        chat_id: str,
        history: List[dict],
        message_count: int,
        top_k: int = 5,
    ) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        print("Handling user message with verification through orchestrator...")
        queryType = self._classifyQuery(user_message)

        if queryType == 'greetings_and_bye':
            reply = self.components.generator.generateSimpleResponse(user_message, queryType=queryType)
            final_reply, aggregated = self._verify(reply)
            return final_reply, aggregated

        # load memory
        summary = self.components.memoryAdapter.getSummary(user_id, chat_id)
        profile = self.components.memoryAdapter.getProfile(user_id, chat_id)

        user_state = self._analyze(user_message)
        _          = self._embed(user_message)
        retrieved  = self._retrieve(user_message, top_k=top_k, queryType=queryType)
        print(f"the retrieved docs are : {retrieved}")

        context = self._buildGeneratorContext(
            user_message, retrieved, user_state,
            queryType=queryType,
            history=history,
            summary=summary,
            user_profile=profile
        )
        print(f"the context for generation is : {context.format_context_for_prompt()}")

        reply = self._generate(context)
        final_reply, aggregated = self._verify(reply, user_state)
        
        # Only summarize if there is history to summarize and at specific intervals
        if message_count > 0 and message_count % 20 == 0:  
            self._summarize(user_id, chat_id, history)

        # --- TEMPORARY ENHANCED JSON EXPORT FOR PROFESSOR ---
        export_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message_count": message_count,
            "current_summary": summary,
            "persistent_profile": profile,
            "analysis_metadata": {
                "detected_emotions": str(user_state.emotions) if user_state and user_state.emotions else [],
                "detected_intents": user_state.intents if user_state and user_state.intents else [],
                "detected_needs": user_state.needs if user_state and user_state.needs else [],
                "verification": {
                    "status": aggregated.status.value if aggregated else "N/A",
                    "scores": aggregated.all_scores if aggregated else {}
                }
            },
            "conversation_history": history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_reply}
            ]
        }
        with open(f"conversation_export_{chat_id}.json", "w") as f:
            json.dump(export_data, f, indent=4)

        # --- ADDITIONAL EXPORT: MESSAGE AND RESPONSE ONLY ---
        simple_export = {
            "user": user_message,
            "assistant": final_reply
        }
        with open(f"message_response_{chat_id}.json", "w") as f:
            json.dump(simple_export, f, indent=4)
        # -------------------------------------------

        self.state = OrchestrationState.COMPLETED
        return final_reply, aggregated