from enum import Enum

class VerificationIssue(Enum):
    SAFETY_CONCERN = "safety_concern"
    LOW_EMPATHY = "low_empathy"
    INAPPROPRIATE_TONE = "inappropriate_tone"
    FACTUAL_INCONSISTENCY = "factual_inconsistency"
    CONTEXT_MISMATCH = "context_mismatch"
    HARMFUL_ADVICE = "harmful_advice"
    INSENSITIVE_CONTENT = "insensitive_content"