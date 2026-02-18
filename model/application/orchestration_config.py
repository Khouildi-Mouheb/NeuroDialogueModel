"""
Orchestration configuration - Application layer configuration.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class OrchestratorConfig:
    """Configuration for chat orchestrator."""
    
    enable_emotion: bool = True
    enable_intent: bool = True
    free_mode: bool = False
    max_retries: int = 1
    disabled_tools: List[str] = None
    
    def __post_init__(self):
        if self.disabled_tools is None:
            self.disabled_tools = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
