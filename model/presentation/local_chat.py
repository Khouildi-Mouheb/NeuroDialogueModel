"""
Local chat presentation - Local/CLI chat interface.
"""
from application.chat_orchestrator import ChatOrchestrator


class LocalChat:
    """Presentation layer for local/CLI chat."""

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

    def chat(self, user_input: str) -> str:
        """Run a chat interaction and return the response."""
        result = self.orchestrator.orchestrate(user_input)
        return result.get("response", "")

    def run_interactive(self):
        """Run an interactive chat loop."""
        print("NeuroDialogue Local Chat - Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            try:
                response = self.chat(user_input)
                print(f"Assistant: {response}\n")
            except Exception as e:
                print(f"Error: {str(e)}\n")
