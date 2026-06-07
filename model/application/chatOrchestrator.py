import re
import json
import os
from typing import Optional, Tuple, List

from domain.services.userState import UserState
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.orchestrationState import OrchestrationState
from domain.memory.enums.coachingStage import CoachingStage
from domain.memory.enums.tagPriority import TagPriority
from domain.valueObjects.aggregatedVerificationResult import AggregatedVerificationResult
from domain.context.generatorContext import GeneratorContext
from domain.context.summaryContext import SummaryContext
from domain.context.profileExtractionContext import ProfileExtractionContext
from domain.entities.query.userQuery import UserQuery
from application.config.systemComponents import SystemComponents


class ChatOrchestrator:

    def __init__(self, components: SystemComponents) -> None:
        self.components = components
        self.state = OrchestrationState.IDLE

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
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
                user_state.intents = result.result['intents']
                user_state.needs   = result.result['needs']
        return user_state

    def _classifyQuery(self, user_message: str) -> Optional[str]:
        for agent in self.components.analysis_agents:
            if hasattr(agent, "classifyQuery"):
                return agent.classifyQuery(user_message)
        return None

    # ------------------------------------------------------------------ #
    # Embedding & retrieval                                                #
    # ------------------------------------------------------------------ #

    def _embed(self, user_message: str):
        self.state = OrchestrationState.EMBEDDING
        return self.components.embedding_model.embedText(user_message)

    def _retrieve(self, user_message: str, top_k: int = 5, queryType: Optional[str] = None) -> list:
        self.state = OrchestrationState.RETRIEVING
        return self.components.retriever.retrieve(user_message, top_k=top_k, queryType=queryType)

    # ------------------------------------------------------------------ #
    # Generation                                                           #
    # ------------------------------------------------------------------ #

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
        user_query = UserQuery(text=user_message, queryType=queryType)
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

    # ------------------------------------------------------------------ #
    # Verification                                                         #
    # ------------------------------------------------------------------ #

    def _verify(self, reply: str, user_state: UserState = None) -> Tuple[str, Optional[AggregatedVerificationResult]]:
        self.state = OrchestrationState.VERIFYING

        if len(self.components.verifiers) < 3:
            return reply, None

        results = {}
        for verifier in self.components.verifiers:
            res  = verifier.verify(reply, user_state=user_state)
            name = verifier.__class__.__name__.lower()
            if "empathy"           in name: results['empathy']         = res
            elif "appropriateness" in name: results['appropriateness'] = res
            elif "safety"          in name: results['safety']          = res
            print(f"Verifier {name} result: {res.status}")

        aggregated = AggregatedVerificationResult(
            empathy=results.get('empathy'),
            appropriateness=results.get('appropriateness'),
            safety=results.get('safety'),
        )

        if aggregated.status == VerificationStatus.REJECTED:
            fallback = aggregated.fallback_response or (
                "I'm sorry, I need to rephrase that. Could you give me a moment?"
            )
            return fallback, aggregated

        return reply, aggregated

    # ------------------------------------------------------------------ #
    # Memory persistence                                                   #
    # ------------------------------------------------------------------ #

    def _persistUserState(self, user_id: str, user_state: UserState) -> None:
        if not user_state:
            return
        if user_state.emotions:
            for emotion in user_state.emotions:
                label     = emotion.get("label") if isinstance(emotion, dict) else str(emotion)
                intensity = emotion.get("score")  if isinstance(emotion, dict) else None
                self.components.memoryAdapter.addEmotion(user_id, label, intensity)
                self.components.memoryAdapter.addStrength(user_id, label, frequency=1)

    def _persistCoachingSession(self, user_id: str, chat_id: str) -> None:
        profile = self.components.memoryAdapter.getUserProfile(user_id)
        stage   = profile.coachingStage if profile else None
        self.components.memoryAdapter.addCoachingSession(
            user_id=user_id,
            chat_id=chat_id,
            coachingStage=CoachingStage(stage) if stage else None,
        )

    def _summarize(self, user_id: str, chat_id: str, history: List[dict]) -> None:
        existing_summary = self.components.memoryAdapter.getSummary(user_id, chat_id)
        existing_profile = self.components.memoryAdapter.getProfile(user_id, chat_id)
        combined_context = f"{existing_summary}\n{existing_profile}" if existing_profile else existing_summary

        # Pass 1: narrative summary
        summary_context = SummaryContext(history=history, existing_summary=combined_context)
        new_memory_raw  = self.components.generator.generateFromPrompt(
            summary_context.format_context_for_prompt(), max_tokens=300
        )
        parts        = re.split(r"Section\s*2[:\-]", new_memory_raw, flags=re.IGNORECASE)
        summary_text = re.sub(r"Section\s*1[:\-]", "", parts[0], flags=re.IGNORECASE).strip()
        profile_text = parts[1].strip() if len(parts) > 1 else "No profile data extracted."

        self.components.memoryAdapter.updateMemory(user_id, chat_id, summary_text, profile_text)

        # Pass 2: structured profile extraction
        profile_context  = ProfileExtractionContext(summary=summary_text, existing_profile=profile_text)
        raw_profile_json = self.components.generator.generateFromPrompt(
            profile_context.format_context_for_prompt(), max_tokens=500
        )
        try:
            extracted = json.loads(raw_profile_json.strip().replace("```json", "").replace("```", ""))
            stage_raw = extracted.get("coachingStage")

            self.components.memoryAdapter.upsertUserProfile(
                user_id=user_id,
                summary=summary_text,
                profile=profile_text,
                preferedCommunicationStyle=extracted.get("preferedCommunicationStyle"),
                emotionalStabilityScore=extracted.get("emotionalStabilityScore"),
                personalityType=extracted.get("personalityType"),
                coachingStage=CoachingStage(stage_raw) if stage_raw else None,
            )

            for tag in extracted.get("coachingTags", []):
                self.components.memoryAdapter.addCoachingTag(user_id, tag, TagPriority.MEDIUM)

            # Update latest coaching session with goal and outcome
            sessions = self.components.memoryAdapter.getCoachingSessions(user_id)
            if sessions:
                latest  = sessions[-1]
                tags    = extracted.get("coachingTags", [])
                self.components.memoryAdapter.updateCoachingSession(
                    session_id=latest.id,
                    goalFocus=tags[0] if tags else None,
                    outcome=summary_text[:200],
                )

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Profile extraction parsing failed: {e}")

    # ------------------------------------------------------------------ #
    # Debug logs                                                           #
    # ------------------------------------------------------------------ #

    def _export_debug_logs(self, user_id: str, chat_id: str, user_state: UserState,
                           aggregated: Optional[AggregatedVerificationResult],
                           user_message: str, final_reply: str) -> None:
        export_data = {
            "user_id":           user_id,
            "chat_id":           chat_id,
            "analysis_metadata": self._build_metadata_dict(user_state, aggregated),
            "memory":            self._collect_memory_snapshot(user_id, chat_id),
        }
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, f"conversation_export_{chat_id}.json"), "w") as f:
                json.dump(export_data, f, indent=4, default=str)
            with open(os.path.join(log_dir, f"message_response_{chat_id}.json"), "w") as f:
                json.dump({"user": user_message, "assistant": final_reply}, f, indent=4)
        except IOError as e:
            print(f"Failed to export debug logs: {e}")

    def _collect_memory_snapshot(self, user_id: str, chat_id: str) -> dict:
        adapter   = self.components.memoryAdapter
        profile   = adapter.getUserProfile(user_id)
        strengths = adapter.getStrengths(user_id)
        tags      = adapter.getCoachingTags(user_id)
        emotions  = adapter.getEmotionHistory(user_id)
        sessions  = adapter.getCoachingSessions(user_id)
        return {
            "conversation_summary": adapter.getSummary(user_id, chat_id),
            "conversation_profile": adapter.getProfile(user_id, chat_id),
            "user_profile": {
                "personalityType":            profile.personalityType            if profile else None,
                "coachingStage":              profile.coachingStage              if profile else None,
                "preferedCommunicationStyle": profile.preferedCommunicationStyle if profile else None,
                "emotionalStabilityScore":    profile.emotionalStabilityScore    if profile else None,
            },
            "strengths": [
                {"emotionLabel": s.emotionLabel, "frequency": s.frequency}
                for s in strengths
            ],
            "coaching_tags": [
                {"tag": t.tag, "priority": t.priority}
                for t in tags
            ],
            "emotion_history": [
                {"emotionLabel": e.emotionLabel, "intensity": e.intensity, "detectedAt": str(e.detectedAt)}
                for e in emotions
            ],
            "coaching_sessions": [
                {
                    "chat_id":      s.chat_id,
                    "coachingStage": s.coachingStage,
                    "goalFocus":    s.goalFocus,
                    "outcome":      s.outcome,
                    "createdAt":    str(s.createdAt),
                }
                for s in sessions
            ],
        }

    def _build_metadata_dict(self, user_state, aggregated):
        return {
            "detected_emotions": str(user_state.emotions) if user_state and user_state.emotions else [],
            "detected_intents":  user_state.intents       if user_state and user_state.intents  else [],
            "detected_needs":    user_state.needs         if user_state and user_state.needs    else [],
            "verification": {
                "status": aggregated.status.value if aggregated else "N/A",
                "scores": aggregated.all_scores   if aggregated else {},
            },
        }

    # ------------------------------------------------------------------ #
    # Public handlers                                                      #
    # ------------------------------------------------------------------ #

    def handleUserMessage(self, user_message: str, top_k: int = 5) -> Tuple[str, None]:
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
        queryType = self._classifyQuery(user_message)

        if queryType == 'greetings_and_bye':
            reply = self.components.generator.generateSimpleResponse(user_message, queryType=queryType)
            final_reply, aggregated = self._verify(reply)
            return final_reply, aggregated

        summary = self.components.memoryAdapter.getSummary(user_id, chat_id)
        profile = self.components.memoryAdapter.getProfile(user_id, chat_id)

        self.components.memoryAdapter.upsertUserProfile(user_id=user_id)

        user_state = self._analyze(user_message)
        self._persistUserState(user_id, user_state)

        _         = self._embed(user_message)
        retrieved = self._retrieve(user_message, top_k=top_k, queryType=queryType)

        context = self._buildGeneratorContext(
            user_message, retrieved, user_state,
            queryType=queryType, history=history,
            summary=summary, user_profile=profile,
        )

        reply                   = self._generate(context)
        final_reply, aggregated = self._verify(reply, user_state)

        self._persistCoachingSession(user_id, chat_id)

        if message_count > 0 and message_count % 10 == 0:
            self._summarize(user_id, chat_id, history)

        self._export_debug_logs(user_id, chat_id, user_state, aggregated, user_message, final_reply)

        self.state = OrchestrationState.COMPLETED
        return final_reply, aggregated