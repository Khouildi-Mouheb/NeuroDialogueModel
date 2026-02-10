import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional

from analysis.domain.userState import UserState
from verification.domain.verificationResult import VerificationResult
from verification.domain.verificationIssue import VerificationIssue
from .verificatorAgent import VerificatorAgent
from verification.domain.verificationResultFactory import VerificationResultFactory

class SafetyVerificator(VerificatorAgent):
    """
    Verificator for safety concerns
    
    Uses toxic-bert model to detect harmful content
    """
    
    def __init__(self, threshold: float = 0.8):
        super().__init__(name="SafetyVerificator")
        
        self.threshold = threshold
        
        # Load safety model
        model_name = "unitary/toxic-bert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def verify(
        self,
        response: str,
        query: str = None,
        user_state: UserState = None
    ) -> VerificationResult:
        """
        Verify response safety
        
        Args:
            response: Response to verify
            query: User query (unused)
            user_state: User state (unused)
            
        Returns:
            VerificationResult with safety assessment
        """
        # Check safety
        safety_score = self._check_safety(response)
        
        scores = {'safety': safety_score}
        
        # Decision logic
        if safety_score >= self.threshold:
            # Safe response
            return VerificationResultFactory.approved(
                scores=scores,
                confidence=safety_score,
                metadata={'verificator': self.name}
            )
        else:
            # Unsafe response
            return VerificationResultFactory.rejected(
                scores=scores,
                issues=[VerificationIssue.SAFETY_CONCERN],
                fallback_response=self._generate_safe_fallback(user_state),
                recommendations=[
                    f"Response contains potentially harmful content (safety score: {safety_score:.2f})",
                    "Consider rephrasing to be more supportive and appropriate"
                ],
                confidence=1.0 - safety_score,
                metadata={'verificator': self.name}
            )
    
    def _check_safety(self, response: str) -> float:
        """
        Check safety using toxic-bert model
        
        Returns:
            Safety score (0-1, higher is safer)
        """
        # Tokenize
        inputs = self.tokenizer(
            response,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
        
        # toxic-bert returns [non-toxic, toxic]
        # We want non-toxic probability
        safety_score = probs[0][0].item()
        
        return safety_score
    
    def _generate_safe_fallback(self, user_state: Optional[UserState]) -> str:
        """Generate a safe fallback response"""
        if user_state and user_state.emotions:
            emotion = user_state.emotions.primary_emotion
            
            if emotion in ['anxiety', 'fear', 'sadness']:
                return (
                    "I want to provide you with the most helpful response possible. "
                    "Let me rephrase that in a more supportive way."
                )
        
        return (
            "I apologize, but I need to reconsider my response to ensure "
            "it's as helpful and appropriate as possible."
        )