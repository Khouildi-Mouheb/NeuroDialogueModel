from typing import List

class Chunk:

    def __init__(self,id : str ="", text: str ="", metadata: list = list[str], start_index: int = 0, end_index: int = 0):
        self.__id=id
        self.__text = text
        self.metadata = metadata if metadata is not None else []
        self.start_index = start_index
        self.end_index = end_index

    def getId(self):
        return self.__id
    
    def setId(self,id):
        self.__id=id

    def getText(self):
        return self.__text
    

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = List[str]()