from dataclasses import dataclass
from typing import Dict , List , Optional
from domain.enums.verificationIssue import VerificationIssue
from domain.enums.verificationStatus import VerificationStatus
from .empathyVerificationResult import EmpathyVerificationResult
from .appropriatenessVerificationResult import AppropriatenessVerificationResult
from .safetyVerificationResult import SafetyVerificationResult

@dataclass
class AggregatedVerificationResult:
    """
    Composite result that holds individual results from every verificator and
    derives an overall verdict from them.

    Rules
    -----
    * If **any** result is REJECTED  → overall status is REJECTED.
    * Else if **any** result is NEEDS_REVISION → overall status is NEEDS_REVISION.
    * Otherwise → overall status is APPROVED.

    The ``fallback_response`` of the first rejected result (if any) is
    surfaced at the top level so callers don't need to dig into child results.
    """

    empathy:          EmpathyVerificationResult
    appropriateness:  AppropriatenessVerificationResult
    safety:           SafetyVerificationResult

    # ------------------------------------------------------------------
    # Derived properties — no extra state needed
    # ------------------------------------------------------------------

    @property
    def status(self) -> VerificationStatus:
        results = [self.empathy, self.appropriateness, self.safety]
        if any(r.is_rejected for r in results):
            return VerificationStatus.REJECTED
        if any(r.needs_fix for r in results):
            return VerificationStatus.NEEDS_REVISION
        return VerificationStatus.APPROVED

    @property
    def is_approved(self) -> bool:
        return self.status == VerificationStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == VerificationStatus.REJECTED

    @property
    def needs_fix(self) -> bool:
        return self.status == VerificationStatus.NEEDS_REVISION

    @property
    def all_scores(self) -> Dict[str, float]:
        """Merged scores dict from all three verificators."""
        return {
            **self.empathy.scores,
            **self.appropriateness.scores,
            **self.safety.scores,
        }

    @property
    def all_issues(self) -> List[VerificationIssue]:
        """Flat list of every issue raised across all verificators."""
        return (
            self.empathy.issues
            + self.appropriateness.issues
            + self.safety.issues
        )

    @property
    def all_recommendations(self) -> List[str]:
        """Flat list of every recommendation across all verificators."""
        return (
            self.empathy.recommendations
            + self.appropriateness.recommendations
            + self.safety.recommendations
        )

    @property
    def fallback_response(self) -> Optional[str]:
        """
        Returns the fallback_response from the first rejected result, if any.
        Only SafetyVerificator sets this today, but the pattern is open to others.
        """
        for result in [self.empathy, self.appropriateness, self.safety]:
            if result.is_rejected and result.fallback_response:
                return result.fallback_response
        return None

    @property
    def average_confidence(self) -> float:
        results = [self.empathy, self.appropriateness, self.safety]
        return sum(r.confidence for r in results) / len(results)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AggregatedVerificationResult("
            f"status={self.status.value}, "
            f"scores={self.all_scores}, "
            f"issues={[i.value for i in self.all_issues]})"
        )
    

    def __repr__(self):
        return (
            f"AggregatedVerificationResult(status={self.status.value}, "
            f"empathy_score={self.empathy.empathy_score:.2f}, "
            f"appropriateness_score={self.appropriateness.appropriateness_score:.2f}, "
            f"safety_score={self.safety.safety_score:.2f}, "
            f"issues={[i.value for i in self.all_issues]})"
        )