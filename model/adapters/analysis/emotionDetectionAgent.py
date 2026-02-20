from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List
import torch
from domain.entities.agent import Agent
from domain.enums.emotionsLabels import EmotionLabels
from domain.valueObjects.emotionResult import EmotionResult
from ports.emotionPort import EmotionPort


class EmotionDetectionAgent(Agent, EmotionPort):

    def __init__(
        self,
        model_name: str = "bhadresh-savani/bert-base-go-emotion",
        emotion_labels: List[EmotionLabels] = None,
    ) -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.emotion_labels: List[EmotionLabels] = emotion_labels or list(EmotionLabels)

    # ------------------------------------------------------------------ #
    # EmotionPort implementation                                           #
    # ------------------------------------------------------------------ #

    def detectEmotions(self, text: str, top_k: int = 3) -> EmotionResult:
        print("start detecting emotions!")
        emotion_result = EmotionResult()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

        top_probs, top_indices = torch.topk(probabilities, top_k)

        for prob, idx in zip(top_probs[0], top_indices[0]):
            emotion: EmotionLabels = self.emotion_labels[idx.item()]
            score: float = prob.item()
            emotion_result.emotions.append(emotion.value)
            emotion_result.emotionsWithScore[emotion.value] = score

        return emotion_result


    def getEmotionalSummary(self, text: str) -> dict:
        emotion_result = self.detect_emotions(text, top_k=5)
        emotions = emotion_result.emotions
        scores = emotion_result.emotionsWithScore

        return {
            "text": text,
            "primary_emotion": emotions[0] if emotions else None,
            "all_emotions": emotions,
            "emotional_intensity": (
                sum(scores.values()) / len(scores) if scores else 0
            ),
        }

    def formatForCoach(self, text: str) -> str:
        emotion_result = self.detect_emotions(text, top_k=3)
        emotions = emotion_result.emotions
        scores = emotion_result.emotionsWithScore

        if not emotions:
            return "Aucune émotion détectée."

        primary = emotions[0]
        message = f"Émotion dominante: {primary} ({scores[primary]:.1%})\n"

        if len(emotions) > 1:
            second, third = emotions[1], emotions[2] if len(emotions) > 2 else None
            message += f"Nuances détectées: {second} ({scores[second]:.1%})"
            if third:
                message += f", {third} ({scores[third]:.1%})"

        return message