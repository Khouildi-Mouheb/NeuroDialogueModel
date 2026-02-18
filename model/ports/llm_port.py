"""
LLM Port - Abstraction for language model generation.

Defines the interface for any LLM provider (cloud-based, local, etc.)
"""
from abc import ABC, abstractmethod
from typing import Iterator


class LLMPort(ABC):
    """Abstract interface for Language Model generation."""

    @abstractmethod
    def stream(self, prompt: str) -> Iterator[str]:
        """
        Stream text generation from the LLM.
        
        Args:
            prompt: Input prompt for generation
            
        Returns:
            Iterator yielding generated text chunks
        """
        pass
