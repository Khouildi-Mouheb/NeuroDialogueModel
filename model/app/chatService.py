from core.domain.userQuery import UserQuery
from analysis.domain.userState import UserState
from core.context.generatorContext import GeneratorContext

class ChatService:

    def __init__(
        self,
        generator,
        emotion_agent,
        intent_agent,
        verification_strategy,
        verificators
    ):
        self.generator = generator
        self.emotion_agent = emotion_agent
        self.intent_agent = intent_agent
        self.verification_strategy = verification_strategy
        self.verificators = verificators

    def generate_response(self, text: str):
        print('view hit')
        # 1. User query
        user_query = UserQuery(text=text)

        # 2. Analysis
        emotions = self.emotion_agent.detect_emotions(text)
        intents = self.intent_agent.analyze(text)

        # 3. User state
        user_state = UserState(
            emotions=emotions,
            intentsAndNeeds=intents
        )

        # 4. Context
        context = GeneratorContext(
            user_query=user_query,
            user_state=user_state
        )
        prompt = context.format_context_for_prompt()

        # 5. Generation (no streaming)
        response = "".join(self.generator.stream(prompt))

        # 6. Verification
        verification = self.verification_strategy.execute(
            verificators=self.verificators,
            response=response,
            query=text,
            user_state=user_state
        )

        # 7. Final response
        if verification.is_approved:
            final = response
        else:
            final = verification.fallback_response or response

        return {
            "response": final,
            "analysis": {
                "emotions": emotions.emotions,
                "emotion_scores": emotions.emotionsWithScore,
                "intents": intents.result,
            },
            "verification": {
                "approved": verification.is_approved,
                "score": verification.overall_score,
                "issues": [i.value for i in verification.issues]
            }
        }
