from domain.ports.queryClassifierPort import QueryClassifierPort
from domain.entities.agent import Agent
from domain.entities.query.userQuery import UserQuery
from typing import List
from domain.enums.queryCategoryMappings import QueryCategoryMappings
from transformers import pipeline


class QueryClassifierAdapter(Agent, QueryClassifierPort):

    def __init__(self, classificationLabels: List[QueryCategoryMappings] = None):
        self.modelName = "cross-encoder/nli-MiniLM2-L6-H768"
        self.classificationLabels = classificationLabels or list(QueryCategoryMappings)
        self.classifier = pipeline(
            task="zero-shot-classification",
            model=self.modelName,
        )

    def classifyQuery(self, query: UserQuery) -> str:
        candidateLabels = [label.value for label in self.classificationLabels]

        result = self.classifier(
            sequences=query.text,
            candidate_labels=candidateLabels,
        )
        return result["labels"][0]