from .context import Context
from typing import Optional


class ProfileExtractionContext(Context):

    def __init__(self, summary: str, existing_profile: Optional[str] = None):
        self.summary          = summary
        self.existing_profile = existing_profile

    def format_context_for_prompt(self) -> str:
        context_parts = []

        context_parts.append(
            "You are a psychological profiling assistant.\n"
            "Based on the conversation summary below, extract structured profile data.\n"
            "Respond ONLY with a valid JSON object. No explanation, no markdown, no backticks."
        )

        if self.existing_profile:
            context_parts.append("── Existing Profile ──")
            context_parts.append(self.existing_profile)

        context_parts.append("── Conversation Summary ──")
        context_parts.append(self.summary)

        context_parts.append(
            "── Output Format ──\n"
            "{\n"
            '  "personalityType": "string or null",\n'
            '  "preferedCommunicationStyle": "string or null",\n'
            '  "coachingStage": "discovery|exploration|goal_setting|action|reflection|closing|null",\n'
            '  "coachingTags": ["tag1", "tag2"],\n'
            '  "emotionalStabilityScore": 0.0\n'
            "}\n\n"
            "Rules:\n"
            "- emotionalStabilityScore is a float between 0.0 (very unstable) and 1.0 (very stable).\n"
            "- coachingTags should reflect the user's main focus areas (e.g. 'anxiety', 'self-confidence', 'career').\n"
            "- If a field cannot be determined from the summary, set it to null.\n"
            "- Carry over fields from the existing profile if still relevant and not contradicted by new data."
        )

        return "\n\n".join(context_parts)