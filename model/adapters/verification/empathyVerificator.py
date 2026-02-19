"""
Empathy Verificator

Checks if response appropriately matches user's emotional state
"""

from typing import Optional

from domain.services.userState import UserState
from domain.valueObjects.empathyVerificationResult import EmpathyVerificationResult
from domain.enums.verificationIssue import VerificationIssue
from .verificatorAgent import VerificatorAgent


class EmpathyVerificator(VerificatorAgent):
    """
    Verificator for empathy alignment with user's emotional state.

    Checks if response tone matches user's emotions.
    """

    def __init__(self, threshold: float = 0.6):
        super().__init__(name="EmpathyVerificator")
        self.threshold = threshold

        self.empathetic_phrases = [
            "i understand", "i hear you", "that sounds", "i can see",
            "it's okay", "you're not alone", "i'm here", "that must be",
            "i appreciate", "thank you for sharing", "i recognize",
        ]
        self.dismissive_phrases = [
            "just", "simply", "all you need", "don't worry",
            "calm down", "relax", "get over", "move on",
        ]

    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None,
    ) -> EmpathyVerificationResult:
        empathy_score = self._check_empathy(response, user_state)
        scores = {"empathy": empathy_score}

        if empathy_score >= self.threshold:
            return EmpathyVerificationResult.approved(
                scores=scores,
                confidence=empathy_score,
                metadata={"verificator": self.name},
            )

        issues = [VerificationIssue.LOW_EMPATHY]
        recommendations = [
            f"Response empathy score is low ({empathy_score:.2f})",
            f"User is experiencing: "
            f"{user_state.emotions.primary_emotion if user_state else 'unknown'}",
        ]

        if self._has_dismissive_language(response):
            issues.append(VerificationIssue.DISMISSIVE_TONE)
            recommendations.append("Response contains dismissive language")

        return EmpathyVerificationResult.needs_revision(
            scores=scores,
            issues=issues,
            recommendations=recommendations,
            confidence=1.0 - empathy_score,
            metadata={"verificator": self.name},
        )

    def _check_empathy(self, response: str, user_state: Optional[UserState]) -> float:
        response_lower = response.lower()
        score = 0.5

        empathetic_count = sum(
            1 for phrase in self.empathetic_phrases if phrase in response_lower
        )
        score += min(empathetic_count * 0.1, 0.3)

        dismissive_count = sum(
            1 for phrase in self.dismissive_phrases if phrase in response_lower
        )
        score -= dismissive_count * 0.2

        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion
            emotion_score = user_state.emotions.get_score(emotion)

            if emotion in ["anxiety", "sadness", "fear", "anger"]:
                if emotion_score > 0.7:
                    score += 0.2 if empathetic_count >= 2 else -0.2

        return max(0.0, min(1.0, score))

    def _has_dismissive_language(self, response: str) -> bool:
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in self.dismissive_phrases)