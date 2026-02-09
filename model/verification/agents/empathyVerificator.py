"""
Empathy Verificator

Checks if response appropriately matches user's emotional state
"""

from typing import Optional
import re

from core.domain.userState import UserState
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from verification.domain.verificationStatus import VerificationStatus
from .verificatorAgent import VerificatorAgent


class EmpathyVerificator(VerificatorAgent):
    """
    Verificator for empathy alignment with user's emotional state
    
    Checks if response tone matches user's emotions
    """
    
    def __init__(self, threshold: float = 0.6):
        super().__init__(name="EmpathyVerificator")
        self.threshold = threshold
        
        # Empathy indicators
        self.empathetic_phrases = [
            "i understand", "i hear you", "that sounds", "i can see",
            "it's okay", "you're not alone", "i'm here", "that must be",
            "i appreciate", "thank you for sharing", "i recognize"
        ]
        
        # Dismissive phrases (red flags)
        self.dismissive_phrases = [
            "just", "simply", "all you need", "don't worry",
            "calm down", "relax", "get over", "move on"
        ]
    
    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Verify empathy alignment
        
        Args:
            response: Response to verify
            query: User query (unused)
            user_state: User state with emotions
            
        Returns:
            VerificationResult with empathy assessment
        """
        # Calculate empathy score
        empathy_score = self._check_empathy(response, user_state)
        
        scores = {'empathy': empathy_score}
        
        # Decision logic
        if empathy_score >= self.threshold:
            # Empathetic response
            return VerificationResultFactory.approved(
                scores=scores,
                confidence=empathy_score,
                metadata={'verificator': self.name}
            )
        else:
            # Lacks empathy
            issues = [VerificationIssue.LOW_EMPATHY]
            recommendations = [
                f"Response empathy score is low ({empathy_score:.2f})",
                f"User is experiencing: {user_state.emotions.primary_emotion if user_state else 'unknown'}"
            ]
            
            # Check for dismissive language
            if self._has_dismissive_language(response):
                issues.append(VerificationIssue.DISMISSIVE_TONE)
                recommendations.append("Response contains dismissive language")
            
            return VerificationResultFactory.needs_revision(
                scores=scores,
                issues=issues,
                recommendations=recommendations,
                confidence=1.0 - empathy_score,
                metadata={'verificator': self.name}
            )
    
    def _check_empathy(
        self,
        response: str,
        user_state: Optional[UserState]
    ) -> float:
        """
        Calculate empathy score
        
        Factors:
        - Presence of empathetic phrases
        - Absence of dismissive phrases
        - Match with user's emotional state
        
        Returns:
            Empathy score (0-1)
        """
        response_lower = response.lower()
        
        # Base score
        score = 0.5
        
        # Check for empathetic phrases
        empathetic_count = sum(
            1 for phrase in self.empathetic_phrases
            if phrase in response_lower
        )
        score += min(empathetic_count * 0.1, 0.3)
        
        # Penalize dismissive phrases
        dismissive_count = sum(
            1 for phrase in self.dismissive_phrases
            if phrase in response_lower
        )
        score -= dismissive_count * 0.2
        
        # Check emotional alignment
        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion
            emotion_score = user_state.emotions.get_score(emotion)
            
            # If user has strong negative emotion, expect more empathy
            if emotion in ['anxiety', 'sadness', 'fear', 'anger']:
                if emotion_score > 0.7:
                    # High negative emotion requires high empathy
                    if empathetic_count >= 2:
                        score += 0.2
                    else:
                        score -= 0.2
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
    
    def _has_dismissive_language(self, response: str) -> bool:
        """Check if response contains dismissive language"""
        response_lower = response.lower()
        return any(
            phrase in response_lower
            for phrase in self.dismissive_phrases
        )