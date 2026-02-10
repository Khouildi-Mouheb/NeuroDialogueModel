
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .verificationStatus import VerificationStatus
from .verificationIssue import VerificationIssue


@dataclass
class VerificationResult:
    """
    Result of response verification process.
    
    Attributes:
        is_approved: Whether the response passed all verification checks
        status: Overall verification status (approved, needs_revision, rejected)
        scores: Dictionary of individual verification scores (0.0 to 1.0)
        issues: List of detected issues, if any
        confidence: Overall confidence in the verification (0.0 to 1.0)
        fallback_response: Alternative response to use if verification fails
        recommendations: Suggestions for improving the response
        metadata: Additional verification metadata
    """
    
    is_approved: bool
    status: VerificationStatus
    scores: Dict[str, float]
    issues: List[VerificationIssue] = field(default_factory=list)
    confidence: float = 1.0
    fallback_response: Optional[str] = None
    recommendations: Optional[List[str]] = field(default_factory=list)
    metadata: Optional[Dict] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and initialize default values"""
        # Ensure confidence is between 0 and 1
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        # Ensure all scores are between 0 and 1
        for key, score in self.scores.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Score '{key}' must be between 0 and 1, got {score}")
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall verification score"""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if any critical issues were detected"""
        return any(issue.is_critical for issue in self.issues)
    
    def get_score(self, category: str, default: float = 0.0) -> float:
        """Safely get a score with a default value"""
        return self.scores.get(category, default)
    
    def add_issue(self, issue: VerificationIssue, recommendation: str = None):
        """Add a verification issue and optional recommendation"""
        if issue not in self.issues:
            self.issues.append(issue)
        if recommendation and recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/serialization"""
        return {
            "is_approved": self.is_approved,
            "status": self.status.value,
            "scores": self.scores,
            "issues": [issue.value for issue in self.issues],
            "confidence": self.confidence,
            "overall_score": self.overall_score,
            "has_critical_issues": self.has_critical_issues,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"VerificationResult("
            f"status={self.status.value}, "
            f"approved={self.is_approved}, "
            f"score={self.overall_score:.2f}, "
            f"issues={len(self.issues)})"
        )


# Factory methods for creating common verification result patterns
class VerificationResultFactory:
    """Factory for creating common verification result patterns"""
    
    @staticmethod
    def approved(
        scores: Dict[str, float],
        confidence: float = 1.0,
        metadata: Dict = None
    ) -> VerificationResult:
        """Create an approved verification result"""
        return VerificationResult(
            is_approved=True,
            status=VerificationStatus.APPROVED,
            scores=scores,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    @staticmethod
    def rejected(
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        fallback_response: str,
        recommendations: List[str] = None,
        confidence: float = 1.0,
        metadata: Dict = None
    ) -> VerificationResult:
        """Create a rejected verification result"""
        return VerificationResult(
            is_approved=False,
            status=VerificationStatus.REJECTED,
            scores=scores,
            issues=issues,
            fallback_response=fallback_response,
            recommendations=recommendations or [],
            confidence=confidence,
            metadata=metadata or {}
        )
    
    @staticmethod
    def needs_revision(
        scores: Dict[str, float],
        issues: List[VerificationIssue],
        recommendations: List[str],
        confidence: float = 1.0,
        metadata: Dict = None
    ) -> VerificationResult:
        """Create a needs-revision verification result"""
        return VerificationResult(
            is_approved=False,
            status=VerificationStatus.NEEDS_REVISION,
            scores=scores,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            metadata=metadata or {}
        )