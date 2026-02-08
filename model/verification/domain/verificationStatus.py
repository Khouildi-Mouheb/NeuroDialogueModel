from enum import Enum


class VerificationStatus(Enum):
    
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"
    
    def __str__(self):
        return self.value
    
    @property
    def is_approved(self) -> bool:

        return self == VerificationStatus.APPROVED
    
    @property
    def requires_action(self) -> bool:
        return self in [VerificationStatus.NEEDS_REVISION, VerificationStatus.REJECTED]