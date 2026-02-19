from dataclasses import dataclass , field
from typing import Any , List 

@dataclass
class SystemComponents:
    embedding_model: Any = None
    retriever: Any = None
    generator: Any = None
    analysis_agents: List[Any] = field(default_factory=list)
    verifiers: List[Any] = field(default_factory=list)
    indexer: Any = None

    def __post_init__(self):
        if len(self.verifiers) not in (0, 3):
            raise ValueError("verifiers must be empty or exactly 3")