from .verificationResult import VerificationResult
from typing import Dict , Optional , List
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.verificationIssue import VerificationIssue


class AppropriatenessVerificationResult(VerificationResult):
    """
    Result produced by AppropriatenessVerificator.

    Relevant score key: ``'appropriateness'``  (float 0-1)
    Possible issues:    INAPPROPRIATE_TONE
    """

    @property
    def appropriateness_score(self) -> float:
        return self.scores.get("appropriateness", 0.0)

    @classmethod
    def approved(                                   # type: ignore[override]
        cls,
        scores: Dict[str, float],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "AppropriatenessVerificationResult":
        return cls(
            status=VerificationStatus.APPROVED,
            scores=scores,
            confidence=confidence,
            metadata=metadata or {},
        )

    @classmethod
    def needs_revision(                             # type: ignore[override]
        cls,
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        recommendations: List[str],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "AppropriatenessVerificationResult":
        return cls(
            status=VerificationStatus.NEEDS_REVISION,
            scores=scores,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata or {},
        )
