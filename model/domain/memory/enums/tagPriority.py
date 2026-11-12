from enum import Enum

class TagPriority(str, Enum):
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"