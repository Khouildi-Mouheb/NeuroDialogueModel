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
            "Your goal is to extract key emotional themes, psychological needs, and persistent user insights.\n"
            "Integrate new information into the existing summary while maintaining the core context of the user's journey.\n"
            "Identify 'Persistent Insights': stable facts about the user (e.g., career, family, core values) and recurring strengths.\n"
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
            "- Section 1: Narrative Summary (Current focus and emotional state).\n"
            "- Section 2: Persistent Insights (Key facts, strengths, and long-term goals).\n"
            "- Do not fabricate anything not present in the messages.\n"
            "- Ensure 'Persistent Insights' are carried over from the previous summary if still relevant.\n"
            "- Keep it under 100 words."
        )

        return "\n\n".join(context_parts)