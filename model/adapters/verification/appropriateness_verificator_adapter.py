"""
Appropriateness Verificator Adapter - Implements VerificationPort for appropriateness checks.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ports.verification_port import VerificationPort
from .verification_models import VerificationResult, VerificationStatus, VerificationIssue


class AppropriatenessVerificatorAdapter(VerificationPort):
    """Concrete implementation of VerificationPort for appropriateness verification."""
    
    def __init__(self, threshold: float = 0.7):
        self.name = "AppropriatenessVerificator"
        self.threshold = threshold
        
        # Load appropriateness model
        model_name = "facebook/bart-large-mnli"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def verify(self, response: str, query: str = None, user_state=None) -> VerificationResult:
        """Verify response appropriateness using BART model."""
        appropriateness_score = self._check_appropriateness(response, query)
        
        scores = {'appropriateness': appropriateness_score}
        
        is_approved = appropriateness_score >= self.threshold
        issues = []
        
        if not is_approved:
            issues.append(VerificationIssue.INAPPROPRIATE_TONE)
        
        status = VerificationStatus.APPROVED if is_approved else VerificationStatus.NEEDS_REVISION
        
        return VerificationResult(
            is_approved=is_approved,
            status=status,
            scores=scores,
            issues=issues,
            confidence=appropriateness_score,
        )
    
    def _check_appropriateness(self, response: str, query: str = None) -> float:
        """Check appropriateness score of response."""
        try:
            inputs = self.tokenizer(response, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                # Use neutral class as appropriateness (simplified)
                appropriateness_score = probs[0][1].item() if len(probs[0]) > 1 else 0.5
                return min(appropriateness_score, 1.0)
        except Exception:
            return 0.5  # Default middle score if model fails
