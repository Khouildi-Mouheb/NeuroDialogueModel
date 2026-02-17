from dataclasses import dataclass


@dataclass
class RetrievalConfig:
    """Configuration for retrieval and chunking components."""
    chunk_size: int = 512
    chunk_overlap: int = 64
    embedding_model: str = "default-embedder"

    def to_dict(self):
        return self.__dict__.copy()
