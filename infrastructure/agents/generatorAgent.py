from abc import abstractmethod
from core.context.generatorContext import GeneratorContext
from .agent import Agent

class GeneratorAgent(Agent):

    @abstractmethod
    def stream(self, context: GeneratorContext):
        pass