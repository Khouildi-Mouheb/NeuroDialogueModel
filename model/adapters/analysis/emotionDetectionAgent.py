from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from domain.entities.agent import Agent
from domain.valueObjects.emotionResult import EmotionResult

class EmotionDetectionAgent(Agent):
    def __init__(self,
                 model_name="bhadresh-savani/bert-base-go-emotion",
                 ):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # GoEmotions 27 emotion labels
        self.emotion_labels = [
            'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
            'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
            'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
            'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
            'relief', 'remorse', 'sadness', 'surprise','neutral'
        ]
    
    def detect_emotions(self, text : str, top_k=3) -> EmotionResult:
        print('start detecting emotions ! ')
        emotionResult=EmotionResult()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get top emotions
        top_probs, top_indices = torch.topk(probabilities, top_k)
        
        
        for prob, idx in zip(top_probs[0], top_indices[0]):
            emotion = self.emotion_labels[idx.item()]
            score = prob.item()
            emotionResult.emotions.append(emotion)
            emotionResult.emotionsWithScore[emotion]=score
        
        return emotionResult
    
    def get_emotional_summary(self, text):
        emotions = self.detect_emotions(text, top_k=5)
        
        summary = {
            'text': text,
            'primary_emotion': emotions[0] if emotions else None,
            'all_emotions': emotions,
            'emotional_intensity': sum(score for _, score in emotions) / len(emotions) if emotions else 0
        }
        
        return summary
    
    def format_for_coach(self, text):
        emotions = self.detect_emotions(text, top_k=3)
        
        # Create coach-friendly message
        if not emotions:
            return "Aucune émotion détectée."
        
        primary = emotions[0]
        nuance_message = f"Émotion dominante: {primary[0]} ({primary[1]:.1%})\n"
        
        if len(emotions) > 1:
            nuance_message += f"Nuances détectées: {emotions[1][0]} ({emotions[1][1]:.1%}), "
            nuance_message += f"{emotions[2][0]} ({emotions[2][1]:.1%})"
        
        return nuance_message