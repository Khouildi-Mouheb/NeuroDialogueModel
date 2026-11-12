from .context import Context
from typing import List


class TitleGenerationContext(Context):

    def __init__(self, history: List[dict]):
        self.history = history

    def format_context_for_prompt(self) -> str:
        context_parts = []

        context_parts.append(
            "You are generating a short title for a coaching conversation.\n"
            "Based on the first exchanges below, generate a concise and meaningful title.\n"
            "The title must be maximum 6 words, no quotes, no punctuation at the end."
        )

        context_parts.append("── Conversation ──")
        for msg in self.history:
            role    = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            context_parts.append(f"{role}: {content}")

        context_parts.append(
            "── Instructions ──\n"
            "- Capture the core theme or emotional focus of the conversation.\n"
            "- Do not use generic titles like 'Coaching Session' or 'Conversation'.\n"
            "- Write only the title, nothing else."
        )

        return "\n\n".join(context_parts)