from abc import abstractmethod
from domain.context.generatorContext import GeneratorContext
from domain.entities.agent import Agent


class GeneratorAgent(Agent):

    @abstractmethod
    def stream(self, context: GeneratorContext):
        pass