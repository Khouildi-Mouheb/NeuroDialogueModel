from abc import ABC, abstractmethod
from typing import Iterator
from domain.context.generatorContext import GeneratorContext


class GenerationPort(ABC):
    """Port (interface) for any text generation adapter.

    Any concrete generator must inherit from this class and implement
    all abstract methods.

    Usage:
        class LocalBasedGenerator(Agent, GenerationPort):
            def stream(self, context) -> Iterator[str]: ...
            def generateFullResponse(self, context) -> str: ...
    """

    @abstractmethod
    def stream(self, context: GeneratorContext) -> Iterator[str]:
        """Stream the generated response token by token.

        Args:
            context: GeneratorContext containing the prompt and metadata.

        Yields:
            str: successive tokens/chunks of the generated response.
        """
        ...

    @abstractmethod
    def generateFullResponse(self, context: GeneratorContext) -> str:
        """Generate the full response in one shot (no streaming).

        Args:
            context: GeneratorContext containing the prompt and metadata.

        Returns:
            str: the complete generated response.
        """
        ...