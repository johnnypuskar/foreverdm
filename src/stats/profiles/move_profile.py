from src.stats.profiles.stat_profile import StatProfile

class MoveProfile(StatProfile):
    def __init__(self, speed, size, creature_type, abilities):
        super().__init__(abilities)
        self._speed = speed
        self._size = size
        self._creature_type = creature_type
    
    def get_profile_data(self) -> str:
        return f"speed({str(self._speed)}) size({str(self._size)}) type({str(self._creature_type)})" + super().get_abilities()