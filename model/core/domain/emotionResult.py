from typing import List ,Dict

class EmotionResult :
    def __init__(self ,
                 emotions : List[str] = list(),
                 emotionsWithScore : Dict[str,float] = dict()
                 ):
        self.emotions =emotions
        self.emotionsWithScore =emotionsWithScore


    def __str__(self):
        return f"the emotions are : {self.emotions}"

