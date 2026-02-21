import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Optional
from domain.services.userState import UserState
from domain.valueObjects.safetyVerificationResult import SafetyVerificationResult
from domain.enums.verificationIssue import VerificationIssue
from adapters.verification.verificatorAgent import VerificatorAgent


class SafetyVerificator(VerificatorAgent):
    """
    Verificator for safety concerns.
    Uses toxic-bert model to detect harmful content.
    """

    def __init__(self, threshold: float = 0.1):
        super().__init__(name="SafetyVerificator")
        self.threshold = threshold

        model_name = "unitary/toxic-bert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

    def verify(
        self,
        response: str,
        query: Optional[str] = None,
        user_state: Optional[UserState] = None,
    ) -> SafetyVerificationResult:
        safety_score = self._check_safety(response)
        scores = {"safety": safety_score}

        if safety_score >= self.threshold:
            return SafetyVerificationResult.approved(
                scores=scores,
                confidence=safety_score,
                metadata={"verificator": self.name},
            )

        return SafetyVerificationResult.rejected(
            scores=scores,
            issues=[VerificationIssue.SAFETY_CONCERN],
            fallback_response=self._generate_safe_fallback(user_state),
            recommendations=[
                f"Response contains potentially harmful content "
                f"(safety score: {safety_score:.2f})",
                "Consider rephrasing to be more supportive and appropriate",
            ],
            confidence=1.0 - safety_score,
            metadata={"verificator": self.name},
        )

    def _check_safety(self, response: str) -> float:
        inputs = self.tokenizer(
            response,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        # toxic-bert: index 0 = non-toxic probability
        return probs[0][0].item()

    def _generate_safe_fallback(self, user_state: Optional[UserState]) -> str:
        if user_state and user_state.emotions:
            if user_state.emotions.primary_emotion in ["anxiety", "fear", "sadness"]:
                return (
                    "I want to provide you with the most helpful response possible. "
                    "Let me rephrase that in a more supportive way."
                )
        return (
            "I apologize, but I need to reconsider my response to ensure "
            "it's as helpful and appropriate as possible."
        )