from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for the generator component."""
    model_name: str = "default-llm"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

    def to_dict(self):
        return self.__dict__.copy()
