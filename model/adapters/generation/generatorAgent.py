from abc import abstractmethod
from domain.context.generatorContext import GeneratorContext
from domain.entities.agent import Agent
from ports.generationPort import GenerationPort


class GeneratorAgent(Agent, GenerationPort):

    @abstractmethod
    def stream(self, context: GeneratorContext):
        pass

    @abstractmethod
    def generateFullResponse(self, context: GeneratorContext):
        pass