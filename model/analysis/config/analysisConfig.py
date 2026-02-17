from dataclasses import dataclass


@dataclass
class AnalysisConfig:
    """Configuration for analysis components (emotion, intent)."""
    # Paths / model ids
    emotion_model: str = "default/emotion-model"
    intent_model: str = "default/intent-model"

    # Behavior
    enable_emotion_postprocessing: bool = True
    intent_confidence_threshold: float = 0.5

    def to_dict(self):
        return self.__dict__.copy()
