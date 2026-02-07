# verification/agents/safetyVerificator.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from .verificatorAgent import VerificatorAgent
from ...infrastructure.verification.domain import VerificationResult, VerificationResultFactory, VerificationIssue

class SafetyVerificator(VerificatorAgent):

    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
        self.model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
        self.threshold = 0.8
    
    def verify(self, query: str, response: str, user_state=None) -> VerificationResult:
        safety_score = self._check_safety(response)
        
        if safety_score >= self.threshold:
            return VerificationResultFactory.approved(
                scores={'safety': safety_score}
            )
        else:
            return VerificationResultFactory.rejected(
                scores={'safety': safety_score},
                issues=[VerificationIssue.SAFETY_CONCERN],
                fallback_response="I apologize, but I need to reconsider my response to ensure it's helpful and appropriate.",
                recommendations=["Response contains potentially harmful content"]
            )
    
    def _check_safety(self, response: str) -> float:
        inputs = self.tokenizer(response, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        return probs[0][0].item()