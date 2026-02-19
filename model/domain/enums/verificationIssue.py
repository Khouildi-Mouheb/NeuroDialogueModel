from enum import Enum

class VerificationIssue(str, Enum):
    # Empathy
    LOW_EMPATHY      = "low_empathy"
    DISMISSIVE_TONE  = "dismissive_tone"
    # Appropriateness
    INAPPROPRIATE_TONE = "inappropriate_tone"
    # Safety
    SAFETY_CONCERN   = "safety_concern"
