from src.util.resettable_value import ResettableValue
from src.util.return_status import ReturnStatus
from server.backend.database.util.data_storer import DataStorer

class HitPoints(DataStorer):
    def __init__(self, hp: int, current_hp: int = None):
        super().__init__()
        self._max_hp = hp
        self.map_data_property("_max_hp", "max_hp")

        self._hp = current_hp if current_hp is not None else hp
        self.map_data_property("_hp", "current_hp")

        self._temp_hp = 0
        self.map_data_property("_temp_hp", "temp_hp")
    
    def get_hp(self):
        """Get current hit points."""
        return self._hp
    
    def add_temp_hp(self, temp_hp: int):
        """
        Adds temporary hit points.
        
        param temp_hp: int - amount of temporary hit points to add.

        returns: ReturnStatus - true if successful, false if not.
        """
        if self._temp_hp < temp_hp:
            self._temp_hp = temp_hp
            return ReturnStatus(True, f"Now have {self._temp_hp} temporary hit points.")
        return ReturnStatus(False, f"Already have {self._temp_hp} temporary hit points.")
    
    def reduce_hp(self, amount: int):
        """
        Removes an amount of hit points, first from temporary hit points then from current hit points.
        Removed health can go into negative values, which is invalid for typical play and must be handled elsewhere.

        param amount: int - amount of hit points to remove.

        returns: ReturnStatus - true if successful, false if not.
        """
        status_message = ""
        if self._temp_hp > 0:
            self._temp_hp -= amount
            if self._temp_hp < 0:
                self._hp += self._temp_hp
                self._temp_hp = 0
            status_message = f" Temporary hit points reduced to {self._temp_hp}."
        else:
            self._hp -= amount
        return ReturnStatus(True, f"Hit points reduced to {self._hp}." + status_message)

    
