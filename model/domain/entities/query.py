"""
Query - Base domain entity for user queries.
"""
from abc import ABC


class Query(ABC):
    def __init__(self, text: str):
        self.text = text
    
    def __str__(self):
        return self.text
