"""
ML Verification Strategy Adapter - Implements VerificationStrategyPort combining multiple verificators.
"""
import logging
from typing import List, Dict
from ports.verification_strategy_port import VerificationStrategyPort
from .verification_models import VerificationResult, VerificationStatus, VerificationIssue

logger = logging.getLogger(__name__)


class MLVerificationStrategyAdapter(VerificationStrategyPort):
    """Concrete implementation of VerificationStrategyPort using ML-based verificators."""
    
    def __init__(
        self,
        score_weights: Dict[str, float] = None,
        enable_fallback: bool = True
    ):
        """
        Initialize strategy
        
        Args:
            score_weights: Weight for each verificator's score
            enable_fallback: Whether to use fallback responses
        """
        self.score_weights = score_weights or {
            'safety': 0.4,
            'empathy': 0.3,
            'appropriateness': 0.3
        }
        self.enable_fallback = enable_fallback
    
    def execute(
        self,
        verificators: List,
        response: str,
        query: str = None,
        user_state = None
    ) -> VerificationResult:
        """
        Execute verification strategy using multiple verificators.
        
        Args:
            verificators: List of verification adapters to run
            response: Response to verify
            query: User query
            user_state: User state
            
        Returns:
            Combined VerificationResult
        """
        logger.info(f"Running {len(verificators)} verificators")
        
        # Collect results from all verificators
        all_scores = {}
        all_issues = []
        all_recommendations = []
        individual_results = []
        
        for verificator in verificators:
            logger.debug(f"Running {verificator.name if hasattr(verificator, 'name') else verificator.__class__.__name__}")
            
            try:
                result = verificator.verify(
                    response=response,
                    query=query,
                    user_state=user_state
                )
                
                individual_results.append(result)
                all_scores.update(result.scores)
                all_issues.extend(result.issues)
                all_recommendations.extend(result.recommendations)
                
                logger.debug(
                    f"{verificator.name if hasattr(verificator, 'name') else verificator.__class__.__name__}: {result.status.value} "
                    f"(score: {result.overall_score:.2f})"
                )
                
            except Exception as e:
                logger.error(f"Error in verificator: {str(e)}")
                # Continue with other verificators
        
        # Calculate weighted overall score
        weighted_score = self._calculate_weighted_score(all_scores)
        
        # Check for critical issues
        has_critical = any(issue.is_critical for issue in all_issues)
        
        # Make final decision
        if has_critical:
            # Critical issue → REJECTED
            status = VerificationStatus.REJECTED
            is_approved = False
            fallback = self._generate_fallback(user_state) if self.enable_fallback else None
            
            logger.warning(f"Response REJECTED due to critical issues")
            
        elif len(all_issues) >= 2:
            # Multiple issues → NEEDS_REVISION
            status = VerificationStatus.NEEDS_REVISION
            is_approved = False
            fallback = None
            
            logger.info(f"Response needs revision ({len(all_issues)} issues)")
            
        elif all_issues:
            # One minor issue → NEEDS_REVISION
            status = VerificationStatus.NEEDS_REVISION
            is_approved = False
            fallback = None
            
            logger.info(f"Response needs minor revision")
            
        else:
            # No issues → APPROVED
            status = VerificationStatus.APPROVED
            is_approved = True
            fallback = None
            
            logger.info(f"Response APPROVED (score: {weighted_score:.2f})")
        
        # Create combined result
        return VerificationResult(
            is_approved=is_approved,
            status=status,
            scores=all_scores,
            issues=list(set(all_issues)),  # Remove duplicates
            confidence=weighted_score,
            fallback_response=fallback,
            recommendations=list(set(all_recommendations)),  # Remove duplicates
            metadata={
                'individual_results': len(individual_results),
                'weights': self.score_weights
            }
        )
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted score across all verificators."""
        if not scores:
            return 0.0
        
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for key, score in scores.items():
            weight = self.score_weights.get(key, 1.0 / len(scores))
            weighted_sum += score * weight
            weight_sum += weight
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def _generate_fallback(self, user_state) -> str:
        """Generate a safe fallback response."""
        if user_state and hasattr(user_state, 'emotions') and user_state.emotions:
            return "I appreciate you reaching out. Let me provide a thoughtful response."
        return "I understand. Let me help with that."
