from transformers import pipeline

class SmartIntentNeedsAgent:

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

    def analyze(self, text: str):
        # Detect intent
        intent_result = self.intent_classifier(text, candidate_labels=self.intent_labels)
        intent = intent_result[0]["label"]

        # Detect psychological needs
        needs_result = self.needs_classifier(text, candidate_labels=self.needs_labels)
        need = needs_result["labels"][0]

        return {
            "text": text,
            "intent": intent,
            "psychological_need": need
        }


