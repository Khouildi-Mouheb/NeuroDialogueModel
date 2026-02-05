from typing import List

class IntentAndNeedsResult:
    def __init__(self,
                 intents : List[str] = None,
                 needs : List[str]= None,
                 ):
        self.result={
            'intents':intents,
            'needs':needs,
        }