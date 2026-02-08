import numpy as np
from sentence_transformers import SentenceTransformer
from core.domain.document import Document

class EmbeddingModel: 

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        #print(f"Loaded embedding model: {model_name} ({self.dimension} dimensions)")
    
    def embedDocument(self, document: Document) -> Document:
        chunks= document.getChunks()
        texts = [chunk.getText() for chunk in chunks]
        embeddings =[]
        for text in texts:
             embedding = self.model.encode(text, convert_to_numpy=True)
             embeddings.append(embedding.tolist())
             document.setEmbeddings(embeddings)
        return document
    
    def embedtext(
                    self,
                    text :str
                    ):
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    
    def embed_batch(self, texts, batch_size=32):

        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
            embeddings.extend(batch_embeddings.tolist())
        
        return embeddings
    
    def get_similarity(self, text1, text2) -> float:
        emb1 = self.embedText(text1)
        emb2 = self.embedText(text2)

        a = np.array(emb1)
        b = np.array(emb2)
        
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return float(similarity)
    
    #get embedding dimension
    def get_dimension(self): 
        return self.dimension

