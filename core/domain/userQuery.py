from core.domain.query import Query

class UserQuery(Query):
    def __init__(self, text: str, user_id: str = None, timestamp: str = None):
        super().__init__(text)
        self.user_id = user_id
        self.timestamp = timestamp
