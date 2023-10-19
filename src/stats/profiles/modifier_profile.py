from src.stats.profiles.stat_profile import StatProfile

class ModifierProfile(StatProfile):
    def __init__(self, name, modifier, abilities):
        super().__init__(abilities)
        self._name = name
        self._modifier = modifier
    
    def get_profile_data(self) -> str:
        return f"{self._name}({'+' if self._modifier >= 0 else ''}{str(self._modifier)})" + super().get_abilities()
