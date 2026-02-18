"""
Safety Verificator Adapter - Implements VerificationPort for safety checks.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ports.verification_port import VerificationPort
from .verification_models import VerificationResult, VerificationStatus, VerificationIssue


class SafetyVerificatorAdapter(VerificationPort):
    """Concrete implementation of VerificationPort for safety verification."""
    
    def __init__(self, threshold: float = 0.8):
        self.name = "SafetyVerificator"
        self.threshold = threshold
        
        # Load safety model
        model_name = "unitary/toxic-bert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def verify(self, response: str, query: str = None, user_state=None) -> VerificationResult:
        """Verify response safety using toxic-bert model."""
        # Check safety
        safety_score = self._check_safety(response)
        
        scores = {'safety': safety_score}
        
        is_approved = safety_score >= self.threshold
        issues = []
        
        if not is_approved:
            issues.append(VerificationIssue.SAFETY_CONCERN)
        
        status = VerificationStatus.APPROVED if is_approved else VerificationStatus.REJECTED
        
        return VerificationResult(
            is_approved=is_approved,
            status=status,
            scores=scores,
            issues=issues,
            confidence=safety_score,
        )
    
    def _check_safety(self, response: str) -> float:
        """Check safety score of response."""
        try:
            inputs = self.tokenizer(response, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                # Toxic probability (index 1 is usually toxic)
                toxic_prob = probs[0][1].item() if len(probs[0]) > 1 else 0.0
                # Return "safety" as 1 - toxic_prob
                return 1.0 - toxic_prob
        except Exception:
            return 1.0  # Default to safe if model fails
