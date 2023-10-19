from src.stats.profiles.stat_profile import StatProfile

class SpellcastProfile(StatProfile):
    def __init__(self, held, slots, spell, abilities):
        super().__init__(abilities)
        self._held = held
        self._slots = slots
        self._spell = spell
    
    def get_profile_data(self) -> str:
        return f"holding{self._held} spell slots({self._slots}) spell({str(self._spell)})" + super().get_abilities()