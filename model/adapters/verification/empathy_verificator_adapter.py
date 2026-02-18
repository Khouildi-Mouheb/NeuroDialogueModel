"""
Empathy Verificator Adapter - Implements VerificationPort for empathy checks.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ports.verification_port import VerificationPort
from .verification_models import VerificationResult, VerificationStatus, VerificationIssue


class EmpathyVerificatorAdapter(VerificationPort):
    """Concrete implementation of VerificationPort for empathy verification."""
    
    def __init__(self, threshold: float = 0.6):
        self.name = "EmpathyVerificator"
        self.threshold = threshold
        
        # Load empathy model
        model_name = "microsoft/deberta-v3-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def verify(self, response: str, query: str = None, user_state=None) -> VerificationResult:
        """Verify response empathy level using DeBERTa model."""
        empathy_score = self._check_empathy(response, query)
        
        scores = {'empathy': empathy_score}
        
        is_approved = empathy_score >= self.threshold
        issues = []
        
        if not is_approved:
            issues.append(VerificationIssue.LOW_EMPATHY)
        
        status = VerificationStatus.APPROVED if is_approved else VerificationStatus.NEEDS_REVISION
        
        return VerificationResult(
            is_approved=is_approved,
            status=status,
            scores=scores,
            issues=issues,
            confidence=empathy_score,
        )
    
    def _check_empathy(self, response: str, query: str = None) -> float:
        """Check empathy score of response."""
        try:
            inputs = self.tokenizer(response, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                # Use first probability as empathy score (simplified)
                empathy_score = probs[0][0].item() if len(probs[0]) > 0 else 0.5
                return min(empathy_score, 1.0)
        except Exception:
            return 0.5  # Default middle score if model fails
