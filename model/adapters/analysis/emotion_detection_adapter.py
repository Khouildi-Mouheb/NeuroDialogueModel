"""
EmotionDetectionAdapter - Adapter implementing EmotionPort using transformers.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ports.emotion_port import EmotionPort
from domain.value_objects.emotion_result import EmotionResult


class EmotionDetectionAdapter(EmotionPort):
    """Concrete implementation of EmotionPort using GoEmotions model."""
    
    def __init__(self, model_name="bhadresh-savani/bert-base-go-emotion"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # GoEmotions 27 emotion labels
        self.emotion_labels = [
            'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
            'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
            'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
            'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
            'relief', 'remorse', 'sadness', 'surprise', 'neutral'
        ]
    
    def detect_emotions(self, text: str, top_k: int = 3) -> EmotionResult:
        """Detect emotions in text using transformer model."""
        print('start detecting emotions ! ')
        emotion_result = EmotionResult()
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
            emotion_result.emotions.append(emotion)
            emotion_result.emotionsWithScore[emotion] = score
        
        return emotion_result
