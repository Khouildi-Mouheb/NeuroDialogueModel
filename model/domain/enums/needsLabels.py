from enum import Enum


class NeedLabel(str, Enum):
    # Cognitive needs
    KNOWLEDGE_UNDERSTANDING = "knowledge/understanding"
    CLARITY                 = "clarity"
    MEANING                 = "meaning/purpose"
    STIMULATION             = "stimulation/curiosity"

    # Emotional needs
    EMOTIONAL_VALIDATION    = "emotional validation"
    EMOTIONAL_SAFETY        = "emotional safety"
    EMPATHY                 = "empathy"
    COMFORT                 = "comfort"
    HOPE                    = "hope"

    # Social needs
    BELONGING_CONNECTION    = "belonging/connection"
    ACCEPTANCE              = "acceptance"
    RECOGNITION             = "recognition"
    TRUST                   = "trust"

    # Autonomy needs
    AUTONOMY                = "autonomy/control"
    SELF_EXPRESSION         = "self-expression"
    COMPETENCE              = "competence/mastery"

    # Support needs
    SUPPORT_ASSISTANCE      = "support/assistance"
    ENCOURAGEMENT           = "encouragement"
    GUIDANCE                = "guidance"
    ACCOUNTABILITY          = "accountability"