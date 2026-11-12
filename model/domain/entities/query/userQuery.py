from .query import Query

class UserQuery(Query):
    def __init__(self, text: str, user_id: str = None, 
                 timestamp: str = None,
                 queryType : str = None):
        super().__init__(text)
        self.user_id = user_id
        self.timestamp = timestamp
        self.queryType = queryType


    def __repr__(self):
        return f"UserQuery(text={self.text}, user_id={self.user_id}, timestamp={self.timestamp}, queryType={self.queryType})"