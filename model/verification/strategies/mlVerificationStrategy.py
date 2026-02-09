"""
ML Verification Strategy

Combines multiple ML-based verificators
"""

from typing import List, Dict
import logging

from core.domain.userState import UserState
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from verification.domain.verificationStatus import VerificationStatus
from verification.agents.verificatorAgent import VerificatorAgent
from .verificationStrategy import VerificationStrategy

logger = logging.getLogger(__name__)


class MLVerificationStrategy(VerificationStrategy):
    """
    Combines multiple ML-based verificators
    
    Strategy:
    1. Run all verificators
    2. Aggregate scores
    3. Collect all issues
    4. Make final decision based on:
       - Critical issues → REJECTED
       - Multiple minor issues → NEEDS_REVISION
       - All pass → APPROVED
    """
    
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
        verificators: List[VerificatorAgent],
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Execute verification with multiple verificators
        
        Args:
            verificators: List of verificators to run
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
            logger.debug(f"Running {verificator.name}")
            
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
                    f"{verificator.name}: {result.status.value} "
                    f"(score: {result.overall_score:.2f})"
                )
                
            except Exception as e:
                logger.error(f"Error in {verificator.name}: {str(e)}")
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
                'strategy': self.__class__.__name__,
                'verificator_count': len(verificators),
                'weighted_score': weighted_score
            }
        )
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted average of scores"""
        if not scores:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for category, score in scores.items():
            weight = self.score_weights.get(category, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_fallback(self, user_state: UserState = None) -> str:
        """Generate fallback response"""
        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion
            
            if emotion in ['anxiety', 'fear']:
                return (
                    "I understand you're feeling anxious. Let me take a moment "
                    "to provide you with a more thoughtful and supportive response."
                )
            elif emotion in ['sadness', 'depression']:
                return (
                    "I hear that you're going through a difficult time. "
                    "Let me reconsider my response to better support you."
                )
            elif emotion == 'anger':
                return (
                    "I recognize you're feeling frustrated. Let me respond "
                    "in a way that's more helpful and understanding."
                )
        
        return (
            "I want to make sure I give you the most helpful and appropriate response. "
            "Let me reconsider my answer."
        )