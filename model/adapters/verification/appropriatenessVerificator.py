
"""
Appropriateness Verificator

Checks if response tone and content are appropriate for context
"""

from typing import Optional

from domain.services.userState import UserState
from  import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from .verificatorAgent import VerificatorAgent
from verification.domain.verificationResultFactory import VerificationResultFactory


class AppropriatenessVerificator(VerificatorAgent):
    """
    Verificator for response appropriateness
    
    Checks if tone, length, and content match the context
    """
    
    def __init__(self, threshold: float = 0.7):
        super().__init__(name="AppropriatenessVerificator")
        self.threshold = threshold
    
    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Verify response appropriateness
        
        Args:
            response: Response to verify
            query: User query for context
            user_state: User state for context
            
        Returns:
            VerificationResult with appropriateness assessment
        """
        # Calculate appropriateness score
        appropriateness_score = self._check_appropriateness(
            response, query, user_state
        )
        
        scores = {'appropriateness': appropriateness_score}
        
        # Decision logic
        if appropriateness_score >= self.threshold:
            # Appropriate response
            return VerificationResultFactory.approved(
                scores=scores,
                confidence=appropriateness_score,
                metadata={'verificator': self.name}
            )
        else:
            # Inappropriate
            issues = [VerificationIssue.INAPPROPRIATE_TONE]
            recommendations = [
                f"Response appropriateness score is low ({appropriateness_score:.2f})"
            ]
            
            # Specific feedback
            if user_state and user_state.emotions:
                emotion = user_state.emotions.primary_emotion
                recommendations.append(
                    f"Consider adjusting tone for user experiencing: {emotion}"
                )
            
            # Check response length
            if len(response.split()) < 10:
                recommendations.append("Response may be too brief")
            elif len(response.split()) > 200:
                recommendations.append("Response may be too lengthy")
            
            return VerificationResultFactory.needs_revision(
                scores=scores,
                issues=issues,
                recommendations=recommendations,
                confidence=1.0 - appropriateness_score,
                metadata={'verificator': self.name}
            )
    
    def _check_appropriateness(
        self,
        response: str,
        query: Optional[str],
        user_state: Optional[UserState]
    ) -> float:
        """
        Calculate appropriateness score
        
        Factors:
        - Response length (not too short/long)
        - Tone matches context
        - Content relevance
        
        Returns:
            Appropriateness score (0-1)
        """
        score = 0.7  # Base score
        
        # Check length
        word_count = len(response.split())
        if 20 <= word_count <= 150:
            score += 0.1  # Good length
        elif word_count < 10:
            score -= 0.2  # Too short
        elif word_count > 250:
            score -= 0.1  # Too long
        
        # Check for question if query was a question
        if query and '?' in query:
            if any(indicator in response.lower() for indicator in ['?', 'would you', 'can i', 'shall we']):
                score += 0.1  # Engages with questions
        
        # Check emotional appropriateness
        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion
            
            # For negative emotions, response should be supportive
            if emotion in ['anxiety', 'sadness', 'fear']:
                supportive_words = ['help', 'support', 'understand', 'here for you']
                if any(word in response.lower() for word in supportive_words):
                    score += 0.1
            
            # For positive emotions, can be more casual
            elif emotion in ['joy', 'excitement']:
                positive_words = ['great', 'wonderful', 'glad', 'happy']
                if any(word in response.lower() for word in positive_words):
                    score += 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
