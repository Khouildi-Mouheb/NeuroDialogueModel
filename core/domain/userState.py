from core.domain.emotionResult import EmotionResult

class UserState: 
        def __init__(self, 
                     emotions: EmotionResult = None
                     ):
            self.emotions = emotions



        def __str__(self):
              return f"the emotions in the user state are : {self.emotions}"