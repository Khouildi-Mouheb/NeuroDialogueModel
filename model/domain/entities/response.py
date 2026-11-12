
class Response:
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return f"the response in {self.content}"
