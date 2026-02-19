from enum import Enum


class IntentLabel(str, Enum):
    # Information seeking
    ASK_INFO            = "ask_info"
    ASK_DEFINITION      = "ask_definition"
    ASK_EXPLANATION     = "ask_explanation"
    ASK_ADVICE          = "ask_advice"
    ASK_RECOMMENDATION  = "ask_recommendation"

    # Emotional expression
    EXPRESS_EMOTION     = "express_emotion"
    EXPRESS_FRUSTRATION = "express_frustration"
    EXPRESS_SADNESS     = "express_sadness"
    EXPRESS_JOY         = "express_joy"
    EXPRESS_FEAR        = "express_fear"
    EXPRESS_GRATITUDE   = "express_gratitude"

    # Help & support
    REQUEST_HELP        = "request_help"
    REQUEST_GUIDANCE    = "request_guidance"
    REQUEST_VALIDATION  = "request_validation"
    REQUEST_MOTIVATION  = "request_motivation"

    # Social
    SOCIAL_CONNECTION   = "social_connection"
    SHARE_EXPERIENCE    = "share_experience"
    VENT                = "vent"

    # Task-oriented
    MAKE_DECISION       = "make_decision"
    SOLVE_PROBLEM       = "solve_problem"
    SET_GOAL            = "set_goal"
    TRACK_PROGRESS      = "track_progress"