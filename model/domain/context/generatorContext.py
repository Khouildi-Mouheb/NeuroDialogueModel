
from .context import Context
from domain.entities.query.userQuery import UserQuery
from domain.entities.knowledge.chunk import Chunk
from domain.services.userState import UserState
from domain.entities.query.rewrittenQuery import RewrittenQuery
from typing import List , Optional

class GeneratorContext(Context):
    def __init__(self, 
                user_query: UserQuery = None, 
                retrieved_chunks: List[Chunk] = None, 
                user_state: UserState = None, 
                rewritten_query: RewrittenQuery = None,
                history: Optional[List[dict]] = None,      
                summary: Optional[str] = None,
                user_profile: Optional[str] = None
                ):
        self.user_query = user_query
        self.retrieved_chunks = retrieved_chunks
        self.user_state = user_state
        self.rewritten_query = rewritten_query
        self.history = history      
        self.summary = summary
        self.user_profile = user_profile
    
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
        "You are Neurodialogue, a compassionate and intelligent emotional support assistant.\n"
        "Your role is to provide empathetic, helpful, and grounded responses using an appreciative coaching approach.\n"
        "This means: lead with strengths, acknowledge what the user is already doing well, use positive and forward-focused language,\n"
        "and help the user discover their own capacities and resources rather than focusing on deficits or problems.\n"
        "Answer ONLY based on the retrieved documents below.\n"
        "If no relevant documents are found, provide a detailed, strengths-focused, and deeply empathetic coaching response.")

        if self.user_state:
            emotions   = getattr(self.user_state, "emotions", None)
            intents    = getattr(self.user_state, "intents", None)
            needs     = getattr(self.user_state, "needs", None)

            if emotions or intents:
                context_parts.append("── User Profile ──")
            if emotions:
                context_parts.append(f"Detected Emotions   : {emotions}")
            if intents:
                context_parts.append(f"Intents and Needs   : {intents}")
            if needs:
                context_parts.append(f"Needs               : {needs}")

        context_parts.append("── Query ──")
        context_parts.append(f"Original Query   : {self.user_query}")
        if self.rewritten_query and self.rewritten_query != self.user_query:
            context_parts.append(f"Rewritten Query  : {self.rewritten_query}")

        if self.user_profile:
            context_parts.append("── User Profile (Long-term) ──")
            context_parts.append(self.user_profile)

        if self.summary:
            context_parts.append("── Conversation Summary ──")
            context_parts.append(self.summary)

        if self.history:
            context_parts.append("── Recent Conversation ──")
            for msg in self.history:
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")

        if self.retrieved_chunks:
            context_parts.append("── Retrieved Documents ──")
            for i, chunk in enumerate(self.retrieved_chunks, 1):
                if isinstance(chunk, dict):
                    text     = chunk.get("text", "").strip()
                    metadata = chunk.get("metadata", {})
                    source   = metadata.get("source", "Unknown")
                    context_parts.append(f"[{i}] Source: {source}\n{text}")
                else:
                    context_parts.append(f"[{i}] {chunk.getText().strip()}")
        else:
            context_parts.append("── Retrieved Documents ──")
            context_parts.append("No relevant documents found.")

        
        context_parts.append(
        "── Instructions ──\n"
        "- Use an appreciative coaching style: highlight strengths, resources, and possibilities.\n"
        "- Open with what the user is doing right or the courage it takes to reach out.\n"
        "- Use forward-focused, generative language (e.g. 'What might help...' rather than 'You should avoid...').\n"
        "- Invite reflection rather than prescribing solutions (e.g. 'What has worked for you before?').\n"
        "- Be empathetic, detailed, and comprehensive in your reflection.\n"
        "- Ground your response in the retrieved documents.\n"
        "- If the user seems distressed, acknowledge their feelings first before moving to strengths.\n"
        "- Never fabricate information.\n"
        "- IMPORTANT: Never mention the documents, chunks, or retrieved information in your response.\n"
        "- Speak naturally as if the knowledge is your own, do not reference any sources or documents."
    )

        return "\n\n".join(context_parts)
