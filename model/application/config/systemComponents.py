from dataclasses import field , dataclass
from typing import Any , List 

@dataclass
class SystemComponents:
    """Shared infrastructure object consumed by all orchestrators.

    ChatOrchestrator uses:
        embedding_model, retriever, generator,
        analysis_agents, verifiers

    EmbeddingOrchestrator uses:
        loader, preprocessor, chunker,
        embedding_model, indexer, vector_store
    """
    embedding_model: Any = None         

    
    retriever:       Any = None   
    generator :      Any =None      
    analysis_agents: List[Any] = field(default_factory=list) 
    verifiers:       List[Any] = field(default_factory=list) 


    loader:       Any = None            
    preprocessor: Any = None           
    chunker:      Any = None           
    indexer:      Any = None           
    vector_store: Any = None           

    def __post_init__(self):
        if self.verifiers and len(self.verifiers) not in (0, 3):
            raise ValueError("verifiers must be empty or exactly 3 — [Empathy, Appropriateness, Safety]")