from src.stats.profiles.stat_profile import StatProfile

class AttackProfile(StatProfile):
    def __init__(self, held, abilities):
        super().__init__(abilities)
        self._held = held
    
    def get_profile_data(self) -> str:
        return f"holding({str(self._held)})" + super().get_abilities()