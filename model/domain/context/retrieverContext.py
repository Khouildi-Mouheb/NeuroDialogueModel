
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from domain.context.context import Context
from domain.entities.query.userQuery import UserQuery
from adapters.retrieval.embedding.embeddingModel import EmbeddingModel



class RetieverContext(Context):
    def __init__(self , userQuery :UserQuery = None):
        self.__userQuery=userQuery
        self.__embeddedQuery=None

    def setUSerQuery(self , query : UserQuery):
        self.__userQuery=query

    def getUserQuery(self):
        return self.__userQuery
    
    def setEmbeddedQuery(self ):
        embeddingModel=EmbeddingModel()
        self.__embeddedQuery=embeddingModel.embedtext(self.__userQuery.text)

    def getEmbeddedQuery(self):
        if self.__embeddedQuery is not None:
            return self.__embeddedQuery
        else:
            self.setEmbeddedQuery()
            return self.__embeddedQuery
        
