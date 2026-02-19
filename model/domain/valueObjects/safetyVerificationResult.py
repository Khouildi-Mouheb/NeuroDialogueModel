from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from .verificationResult import VerificationResult
from domain.enums.verificationIssue import VerificationIssue
from domain.enums.verificationStatus import VerificationStatus



class SafetyVerificationResult(VerificationResult):
    """
    Result produced by SafetyVerificator.

    Relevant score key: ``'safety'``  (float 0-1, higher = safer)
    Possible issues:    SAFETY_CONCERN
    """

    @property
    def safety_score(self) -> float:
        return self.scores.get("safety", 0.0)

    @classmethod
    def approved(                                   # type: ignore[override]
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
    def rejected(                                   # type: ignore[override]
        cls,
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        recommendations: List[str],
        confidence: float,
        fallback_response: Optional[str] = None,
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


