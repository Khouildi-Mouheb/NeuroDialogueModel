from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OrchestratorConfig:
    """Configuration for ChatOrchestrator.

    Fields mirror the dict keys the orchestrator accepts and provide a
    typed object that can be passed into `ChatOrchestrator`.
    """
    enable_emotion: bool = True
    enable_intent: bool = True
    free_mode: bool = False
    max_retries: int = 1
    disabled_tools: Optional[List[str]] = None

    def to_dict(self):
        return {
            "enable_emotion": self.enable_emotion,
            "enable_intent": self.enable_intent,
            "free_mode": self.free_mode,
            "max_retries": self.max_retries,
            "disabled_tools": self.disabled_tools or [],
        }
