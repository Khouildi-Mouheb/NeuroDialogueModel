"""
Verification domain entities moved to adapters.
These are implementation details specific to the verification subsystem.
"""
from enum import Enum


class VerificationStatus(Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"
    
    def __str__(self):
        return self.value
    
    @property
    def is_approved(self) -> bool:
        return self == VerificationStatus.APPROVED
    
    @property
    def requires_action(self) -> bool:
        return self in [VerificationStatus.NEEDS_REVISION, VerificationStatus.REJECTED]


class VerificationIssue(Enum):
    # Safety issues
    SAFETY_CONCERN = "safety_concern"
    HARMFUL_ADVICE = "harmful_advice"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    
    # Empathy issues
    LOW_EMPATHY = "low_empathy"
    DISMISSIVE_TONE = "dismissive_tone"
    INSENSITIVE_CONTENT = "insensitive_content"
    
    # Appropriateness issues
    INAPPROPRIATE_TONE = "inappropriate_tone"
    CONTEXT_MISMATCH = "context_mismatch"
    TONE_MISMATCH = "tone_mismatch"
    
    # Factual issues
    FACTUAL_INCONSISTENCY = "factual_inconsistency"
    HALLUCINATION = "hallucination"
    
    # General issues
    POOR_QUALITY = "poor_quality"
    OFF_TOPIC = "off_topic"
    
    def __str__(self):
        return self.value
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue requiring rejection"""
        critical_issues = {
            VerificationIssue.SAFETY_CONCERN,
            VerificationIssue.HARMFUL_ADVICE,
            VerificationIssue.INAPPROPRIATE_CONTENT
        }
        return self in critical_issues


from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
