from enum import Enum

class CoachingStage(str, Enum):
    DISCOVERY    = "discovery"      # understanding the user's situation
    EXPLORATION  = "exploration"    # identifying strengths and needs
    GOAL_SETTING = "goal_setting"   # defining actionable goals
    ACTION       = "action"         # working toward goals
    REFLECTION   = "reflection"     # reviewing progress
    CLOSING      = "closing"        # wrapping up the coaching arc