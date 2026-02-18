"""
EmotionResult - Value object representing emotion detection results.
"""
from typing import List, Dict


class EmotionResult:
    def __init__(self,
                 emotions: List[str] = None,
                 emotionsWithScore: Dict[str, float] = None
                 ):
        self.emotions = emotions if emotions is not None else []
        self.emotionsWithScore = emotionsWithScore if emotionsWithScore is not None else {}
    
    @property
    def primary_emotion(self) -> str:
        """
        Get the primary (first) emotion
        
        Returns:
            str: Primary emotion, or 'neutral' if no emotions detected
        """
        if self.emotions and len(self.emotions) > 0:
            return self.emotions[0]
        return "neutral"
    
    def get_score(self, emotion: str, default: float = 0.0) -> float:
        """
        Get the score for a specific emotion
        
        Args:
            emotion: Name of the emotion
            default: Default value if emotion not found
            
        Returns:
            float: Emotion score (0.0 to 1.0)
        """
        return self.emotionsWithScore.get(emotion, default)
    
    def __str__(self):
        return f"the emotions are : {self.emotions}"
