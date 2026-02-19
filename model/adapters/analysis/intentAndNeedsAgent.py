from transformers import pipeline
from typing import List
from domain.entities.agent import Agent
from domain.enums.intentLabels import IntentLabel
from domain.enums.needsLabels import NeedLabel
from domain.valueObjects.intentAndNeedsResult import IntentAndNeedsResult
from ports.intentAndNeedsPort import IntentAndNeedsPort


class IntentNeedsAgent(Agent, IntentAndNeedsPort):

    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        intent_labels: List[IntentLabel] = None,
        need_labels: List[NeedLabel] = None,
        top_k_intents: int = 3,
        top_k_needs: int = 3,
    ) -> None:
        self.intent_classifier = pipeline("zero-shot-classification", model=model_name)
        self.needs_classifier  = pipeline("zero-shot-classification", model=model_name)

        self.intent_labels: List[IntentLabel] = intent_labels or list(IntentLabel)
        self.need_labels: List[NeedLabel]     = need_labels   or list(NeedLabel)

        self.top_k_intents = top_k_intents
        self.top_k_needs   = top_k_needs


    def analyze(self, text: str) -> IntentAndNeedsResult:
        """Run both detections and return a combined result."""
        print("start analyzing the intent and needs!")
        return IntentAndNeedsResult(
            intents=self.detectIntents(text),
            needs=self.detectNeeds(text),
        )


    def detectIntents(self, text: str, top_k: int = None) -> List[str]:
        """Detect user intents from text independently of needs.

        Args:
            text:  Raw user input.
            top_k: Number of top intents to return.
                   Defaults to self.top_k_intents if not provided.

        Returns:
            List of top intent label values sorted by descending score.
        """
        print("start detecting intents!")
        k = top_k or self.top_k_intents
        result = self.intent_classifier(
            text,
            candidate_labels=[label.value for label in self.intent_labels],
        )
        return result["labels"][:k]

    def detectNeeds(self, text: str, top_k: int = None) -> List[str]:
        """Detect psychological needs from text independently of intents.

        Args:
            text:  Raw user input.
            top_k: Number of top needs to return.
                   Defaults to self.top_k_needs if not provided.

        Returns:
            List of top need label values sorted by descending score.
        """
        print("start detecting needs!")
        k = top_k or self.top_k_needs
        result = self.needs_classifier(
            text,
            candidate_labels=[need.value for need in self.need_labels],
        )
        return result["labels"][:k]