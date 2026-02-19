from enum import Enum


class VerificationStatus(str, Enum):
    APPROVED       = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED       = "rejected"