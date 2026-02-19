from .verificationResult import VerificationResult
from typing import Dict , Optional , List
from domain.enums.verificationStatus import VerificationStatus
from domain.enums.verificationIssue import VerificationIssue

class EmpathyVerificationResult(VerificationResult):
    """
    Result produced by EmpathyVerificator.

    Relevant score key: ``'empathy'``  (float 0-1, higher = more empathetic)
    Possible issues:    LOW_EMPATHY, DISMISSIVE_TONE
    """

    @property
    def empathy_score(self) -> float:
        return self.scores.get("empathy", 0.0)

    @classmethod
    def approved(                                   # type: ignore[override]
        cls,
        scores: Dict[str, float],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "EmpathyVerificationResult":
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
    ) -> "EmpathyVerificationResult":
        return cls(
            status=VerificationStatus.NEEDS_REVISION,
            scores=scores,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata or {},
        )
