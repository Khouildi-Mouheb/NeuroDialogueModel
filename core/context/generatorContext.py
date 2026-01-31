from .context import Context
from core.domain.userQuery import UserQuery
from core.domain.chunk import Chunk
from core.domain.userState import UserState
from core.domain.rewrittenQuery import RewrittenQuery
from typing import List

class GeneratorContext(Context):
    def __init__(self, 
                 user_query: UserQuery =None, 
                 retrieved_chunks: List[Chunk] = None, 
                 user_state: UserState = None , 
                 rewritten_query: RewrittenQuery = None
                 ):
        self.user_query = user_query
        self.retrieved_chunks = retrieved_chunks
        self.user_state = user_state
        self.rewritten_query = rewritten_query
    
    def get_user_query(self) -> UserQuery:
        return self.user_query
    
    def get_retrieved_chunks(self) -> List[Chunk]:
        return self.retrieved_chunks
    
    def get_user_state(self) -> UserState:
        return self.user_state
    
    def get_rewritten_query(self) -> RewrittenQuery:
        return self.rewritten_query
    
    def format_context_for_prompt(self) -> str:
        context_parts = []
        context_parts.append(
        "answer the query based on the retrieved docs . if theirs now relevant docs , answer in two lines"
        )
        context_parts.append(f"User Query: {self.user_query}")
        if self.rewritten_query:
            context_parts.append(f"Rewritten Query: {self.rewritten_query}")
        if self.retrieved_chunks:
            context_parts.append("Retrieved Information:")
            for i, chunk in enumerate(self.retrieved_chunks, 1):
                context_parts.append(f"Chunk {i}: {chunk.getText()}")
        if self.user_state:
            context_parts.append(f"User State: {self.user_state}")
        return "\n\n".join(context_parts)
