"""
User State Service - Domain service for managing user state.
"""
from ..value_objects.user_state import UserState


class UserStateService:
    """Domain service for user state management."""
    
    @staticmethod
    def create_user_state(emotions, intents_and_needs):
        """Create a user state from emotions and intents."""
        return UserState(
            emotions=emotions,
            intentsAndNeeds=intents_and_needs
        )
