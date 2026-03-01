from abc import ABC , abstractmethod
from domain.entities.query.userQuery import UserQuery   

class QueryClassifierPort(ABC):

    def classifyQuery(self,
                      query : UserQuery = None) -> str:
        pass