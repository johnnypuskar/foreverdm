from src.stats.profiles.stat_profile import StatProfile

class AttackedProfile(StatProfile):
    def __init__(self, armor_class, resistances, immunities, abilities):
        super().__init__(abilities)
        self._armor_class = armor_class
        self._resistances = resistances
        self._immunities = immunities
    
    def get_profile_data(self) -> str:
        return f"armor class({str(self._armor_class)})" + (f" resistances{self._resistances}" if self._resistances else "") + (f" immunities{self._immunities}" if self._immunities else "") + super().get_abilities()