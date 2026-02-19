"""
Appropriateness Verificator

Checks if response tone and content are appropriate for context
"""

from typing import Optional

from domain.services.userState import UserState
from domain.valueObjects.appropriatenessVerificationResult import AppropriatenessVerificationResult
from domain.enums.verificationIssue import VerificationIssue
from .verificatorAgent import VerificatorAgent


class AppropriatenessVerificator(VerificatorAgent):
    """
    Verificator for response appropriateness.

    Checks if tone, length, and content match the context.
    """

    def __init__(self, threshold: float = 0.7):
        super().__init__(name="AppropriatenessVerificator")
        self.threshold = threshold

    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None,
    ) -> AppropriatenessVerificationResult:
        appropriateness_score = self._check_appropriateness(response, query, user_state)
        scores = {"appropriateness": appropriateness_score}

        if appropriateness_score >= self.threshold:
            return AppropriatenessVerificationResult.approved(
                scores=scores,
                confidence=appropriateness_score,
                metadata={"verificator": self.name},
            )

        issues = [VerificationIssue.INAPPROPRIATE_TONE]
        recommendations = [
            f"Response appropriateness score is low ({appropriateness_score:.2f})"
        ]

        if user_state and user_state.emotions:
            recommendations.append(
                f"Consider adjusting tone for user experiencing: "
                f"{user_state.emotions.primary_emotion}"
            )

        word_count = len(response.split())
        if word_count < 10:
            recommendations.append("Response may be too brief")
        elif word_count > 200:
            recommendations.append("Response may be too lengthy")

        return AppropriatenessVerificationResult.needs_revision(
            scores=scores,
            issues=issues,
            recommendations=recommendations,
            confidence=1.0 - appropriateness_score,
            metadata={"verificator": self.name},
        )

    def _check_appropriateness(
        self,
        response: str,
        query: Optional[str],
        user_state: Optional[UserState],
    ) -> float:
        score = 0.7

        word_count = len(response.split())
        if 20 <= word_count <= 150:
            score += 0.1
        elif word_count < 10:
            score -= 0.2
        elif word_count > 250:
            score -= 0.1

        if query and "?" in query:
            if any(
                indicator in response.lower()
                for indicator in ["?", "would you", "can i", "shall we"]
            ):
                score += 0.1

        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion

            if emotion in ["anxiety", "sadness", "fear"]:
                if any(
                    w in response.lower()
                    for w in ["help", "support", "understand", "here for you"]
                ):
                    score += 0.1

            elif emotion in ["joy", "excitement"]:
                if any(
                    w in response.lower()
                    for w in ["great", "wonderful", "glad", "happy"]
                ):
                    score += 0.1

        return max(0.0, min(1.0, score))