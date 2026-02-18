"""
RewrittenQuery - Domain entity for transformed/rewritten queries.
"""
from .query import Query


class RewrittenQuery(Query):
    def __init__(self, text: str, original_query: Query = None):
        super().__init__(text)
        self.original_query = original_query
