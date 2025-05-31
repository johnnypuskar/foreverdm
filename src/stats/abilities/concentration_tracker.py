from src.events.observer import Emitter
from src.util.constants import EventType
from server.backend.database.util.data_storer import DataStorer

class ConcentrationTracker(Emitter, DataStorer):
    def __init__(self):
        super().__init__()
        self._ability_uuid = None
        self._remaining_ticks = 0

        self.map_data_property("_ability_uuid", "ability_uuid")
        self.map_data_property("_remaining_ticks", "remaining_ticks")
    
    @property
    def concentrating(self):
        return self._ability is not None

    def set_concentration(self, ability_uuid, duration):
        if self._ability_uuid is not None:
            self.end_concentration()
        self._ability_uuid = ability_uuid
        self._remaining_ticks = duration
    
    def end_concentration(self):
        if self._ability_uuid is not None:
            self.emit(EventType.ABILITY_CONCENTRATION_ENDED, self._ability_uuid)
            self._ability_uuid = None
            self._remaining_ticks = 0

    def tick_timer(self):
        if self._remaining_ticks > 0:
            self._remaining_ticks -= 1
            if self._remaining_ticks <= 0:
                self.end_concentration()