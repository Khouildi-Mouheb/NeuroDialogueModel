from .context import Context
from typing import List, Optional

class SummaryContext(Context):
    def __init__(self,
                 history: List[dict] = None,
                 existing_summary: Optional[str] = None
                 ):
        self.history = history
        self.existing_summary = existing_summary

    def format_context_for_prompt(self) -> str:
        context_parts = []

        context_parts.append(
            "You are summarizing a coaching conversation.\n"
            "Your goal is to extract the key emotional themes, psychological needs, and topics discussed.\n"
            "Integrate new information into the existing summary while maintaining the core context of the user's journey.\n"
            "Be concise and neutral. Keep the summary under 100 words."
        )

        if self.existing_summary:
            context_parts.append("── Previous Summary ──")
            context_parts.append(self.existing_summary)

        if self.history:
            context_parts.append("── Recent Messages ──")
            for msg in self.history:
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")

        context_parts.append(
            "── Instructions ──\n"
            "- Write a concise summary of the conversation so far.\n"
            "- Focus on emotional themes, expressed needs, and coaching topics.\n"
            "- Do not fabricate anything not present in the messages.\n"
            "- Keep it under 100 words."
        )

        return "\n\n".join(context_parts)