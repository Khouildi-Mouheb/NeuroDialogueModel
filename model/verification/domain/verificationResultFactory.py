"""
Factory for creating VerificationResult objects

Provides convenient methods to create common verification result patterns
"""

from typing import Dict, List, Optional
from .verificationResult import VerificationResult
from .verificationStatus import VerificationStatus
from .verificationIssue import VerificationIssue


class VerificationResultFactory:
    """
    Factory for creating common verification result patterns
    
    Provides three main creation methods:
    - approved(): For responses that pass all checks
    - rejected(): For responses with critical issues
    - needs_revision(): For responses with minor issues
    """
    
    @staticmethod
    def approved(
        scores: Dict[str, float],
        confidence: float = 1.0,
        metadata: Dict = None
    ) -> VerificationResult:
        """
        Create an approved verification result
        
        Args:
            scores: Verification scores (e.g., {'safety': 0.95, 'empathy': 0.82})
            confidence: Confidence in verification (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            VerificationResult with approved status
            
        Example:
            result = VerificationResultFactory.approved(
                scores={'safety': 0.95, 'empathy': 0.85},
                confidence=0.90
            )
        """
        return VerificationResult(
            is_approved=True,
            status=VerificationStatus.APPROVED,
            scores=scores,
            issues=[],
            confidence=confidence,
            fallback_response=None,
            recommendations=[],
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
        """
        Create a rejected verification result
        
        Args:
            scores: Verification scores (e.g., {'safety': 0.30})
            issues: List of detected issues
            fallback_response: Safe fallback response to use
            recommendations: Suggestions for improvement
            confidence: Confidence in verification (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            VerificationResult with rejected status
            
        Example:
            result = VerificationResultFactory.rejected(
                scores={'safety': 0.30},
                issues=[VerificationIssue.SAFETY_CONCERN],
                fallback_response="I need to reconsider my response.",
                recommendations=["Response contains harmful content"]
            )
        """
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
        """
        Create a needs-revision verification result
        
        Args:
            scores: Verification scores (e.g., {'empathy': 0.55})
            issues: List of detected issues
            recommendations: Suggestions for improvement
            confidence: Confidence in verification (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            VerificationResult with needs_revision status
            
        Example:
            result = VerificationResultFactory.needs_revision(
                scores={'empathy': 0.55},
                issues=[VerificationIssue.LOW_EMPATHY],
                recommendations=["Add more empathetic language"]
            )
        """
        return VerificationResult(
            is_approved=False,
            status=VerificationStatus.NEEDS_REVISION,
            scores=scores,
            issues=issues,
            fallback_response=None,
            recommendations=recommendations,
            confidence=confidence,
            metadata=metadata or {}
        )