from enum import Enum


class OrchestrationState(str, Enum):
    IDLE         = "idle"

    ANALYZING    = "analyzing"
    EMBEDDING    = "embedding"
    RETRIEVING   = "retrieving"
    PROMPTING    = "prompting"
    GENERATING   = "generating"
    VERIFYING    = "verifying"

    COMPLETED    = "completed"
    FAILED       = "failed"