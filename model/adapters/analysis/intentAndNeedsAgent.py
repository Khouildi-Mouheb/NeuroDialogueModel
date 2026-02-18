from transformers import pipeline
from typing import List
from domain.valueObjects.intentAndNeedsResult import IntentAndNeedsResult

class IntentNeedsAgent:

    def __init__(self):
        self.intent_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
        self.needs_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        # Define candidate labels for intents and needs
        self.intent_labels = ["ask_info", "express_emotion", "request_help", "social_connection"]
        self.needs_labels = [
            "knowledge/understanding",
            "emotional validation",
            "support/assistance",
            "belonging/connection"
        ]

    def analyze(self, text: str) -> IntentAndNeedsResult:
        print('start analyzing the intent and needs!')
        
        # Detect intent
        intent_result = self.intent_classifier(text, candidate_labels=self.intent_labels)
        
        # Get top 3 intents with their scores
        intents_list = []
        for item in intent_result:
            intents_list.append(item["label"])
        
        # Detect psychological needs
        needs_result = self.needs_classifier(text, candidate_labels=self.needs_labels)
        
        # Get top 3 needs with their scores
        needs_list = needs_result["labels"][:3]  # Top 3 needs
        
        # Create and return IntentAndNeedsResult object
        return IntentAndNeedsResult(
            intents=intents_list,
            needs=needs_list
        )