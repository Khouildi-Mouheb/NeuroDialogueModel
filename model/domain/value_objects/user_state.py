"""
UserState - Value object representing user's emotional and intent state.
"""
from typing import Optional
from .emotion_result import EmotionResult
from .intent_and_needs_result import IntentAndNeedsResult


class UserState:
    def __init__(self, 
                 emotions: Optional[EmotionResult] = None,
                 intentsAndNeeds: Optional[IntentAndNeedsResult] = None,
                 ):
        self.emotions = emotions
        self.intentsAndNeeds = intentsAndNeeds
        self.intents = intentsAndNeeds.result['intents'] if intentsAndNeeds else []
        self.needs = intentsAndNeeds.result['needs'] if intentsAndNeeds else []

    def __str__(self):
        emotions_str = str(self.emotions) if self.emotions else "No emotions detected"
        intents_str = f"Intents: {self.intents}" if self.intents else "No intents detected"
        needs_str = f"Needs: {self.needs}" if self.needs else "No needs detected"
        
        return f"UserState:\n- Emotions: {emotions_str}\n- {intents_str}\n- {needs_str}"
