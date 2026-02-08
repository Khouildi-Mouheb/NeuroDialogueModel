from enum import Enum


class VerificationIssue(Enum):
    
    # Safety issues
    SAFETY_CONCERN = "safety_concern"
    HARMFUL_ADVICE = "harmful_advice"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    
    # Empathy issues
    LOW_EMPATHY = "low_empathy"
    DISMISSIVE_TONE = "dismissive_tone"
    INSENSITIVE_CONTENT = "insensitive_content"
    
    # Appropriateness issues
    INAPPROPRIATE_TONE = "inappropriate_tone"
    CONTEXT_MISMATCH = "context_mismatch"
    TONE_MISMATCH = "tone_mismatch"
    
    # Factual issues
    FACTUAL_INCONSISTENCY = "factual_inconsistency"
    HALLUCINATION = "hallucination"
    
    # General issues
    POOR_QUALITY = "poor_quality"
    OFF_TOPIC = "off_topic"
    
    def __str__(self):
        return self.value
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue requiring rejection"""
        critical_issues = {
            VerificationIssue.SAFETY_CONCERN,
            VerificationIssue.HARMFUL_ADVICE,
            VerificationIssue.INAPPROPRIATE_CONTENT
        }
        return self in critical_issues