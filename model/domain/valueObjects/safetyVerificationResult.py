from typing import Dict, List, Optional
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.verificationIssue import VerificationIssue
from .verificationResult import VerificationResult


class SafetyVerificationResult(VerificationResult):
    """
    Result produced by SafetyVerificator.

    Relevant score key: ``'safety'``  (float 0-1, higher = safer)
    Possible issues:    SAFETY_CONCERN
    Only verificator that can produce REJECTED status.
    """

    @property
    def safety_score(self) -> float:
        return self.scores.get("safety", 0.0)

    @classmethod
    def approved(
        cls,
        scores: Dict[str, float],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "SafetyVerificationResult":
        return cls(
            status=VerificationStatus.APPROVED,
            scores=scores,
            confidence=confidence,
            metadata=metadata or {},
        )

    @classmethod
    def rejected(
        cls,
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        fallback_response: Optional[str],
        recommendations: List[str],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "SafetyVerificationResult":
        return cls(
            status=VerificationStatus.REJECTED,
            scores=scores,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            fallback_response=fallback_response,
            metadata=metadata or {},
        )