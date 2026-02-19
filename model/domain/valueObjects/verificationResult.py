from dataclasses import dataclass , field
from domain.enums.verificationIssue import VerificationIssue
from domain.enums.verificationStatus import VerificationStatus
from typing import Dict , List , Optional
@dataclass
class VerificationResult:
    """
    Base value object returned by every verificator agent.

    Attributes:
        status:           Overall verdict for this verificator.
        scores:           Dict of metric-name → float score (0-1).
        confidence:       How confident the verificator is in its verdict (0-1).
        issues:           List of detected issues (empty when approved).
        recommendations:  Human-readable suggestions for improvement.
        fallback_response: Optional safe replacement text (used by SafetyVerificator).
        metadata:         Arbitrary extra data (e.g. verificator name).
    """

    status:            VerificationStatus
    scores:            Dict[str, float]
    confidence:        float
    issues:            List[VerificationIssue] = field(default_factory=list)
    recommendations:   List[str]               = field(default_factory=list)
    fallback_response: Optional[str]           = None
    metadata:          Dict                    = field(default_factory=dict)


    @classmethod
    def approved(
        cls,
        scores: Dict[str, float],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "VerificationResult":
        return cls(
            status=VerificationStatus.APPROVED,
            scores=scores,
            confidence=confidence,
            metadata=metadata or {},
        )

    @classmethod
    def needs_revision(
        cls,
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        recommendations: List[str],
        confidence: float,
        metadata: Optional[Dict] = None,
    ) -> "VerificationResult":
        return cls(
            status=VerificationStatus.NEEDS_REVISION,
            scores=scores,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata or {},
        )

    @classmethod
    def rejected(
        cls,
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        recommendations: List[str],
        confidence: float,
        fallback_response: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> "VerificationResult":
        return cls(
            status=VerificationStatus.REJECTED,
            scores=scores,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            fallback_response=fallback_response,
            metadata=metadata or {},
        )

    @property
    def is_approved(self) -> bool:
        return self.status == VerificationStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == VerificationStatus.REJECTED

    @property
    def needs_fix(self) -> bool:
        return self.status == VerificationStatus.NEEDS_REVISION
