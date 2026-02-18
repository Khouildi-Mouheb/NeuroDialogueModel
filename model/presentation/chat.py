"""
Chat presentation - Alternative chat service wrapper.
"""
from application.chat_orchestrator import ChatOrchestrator


class ChatService:
    """Presentation layer service wrapping the orchestrator."""

    def __init__(
        self,
        llm_port,
        emotion_port,
        intent_port,
        verification_strategy_port,
        verificators
    ):
        self.orchestrator = ChatOrchestrator(
            llm_port=llm_port,
            emotion_port=emotion_port,
            intent_port=intent_port,
            verification_strategy_port=verification_strategy_port,
            verificators=verificators
        )

    def generate_response(self, text: str):
        """Generate a response for the given text."""
        return self.orchestrator.orchestrate(text)
