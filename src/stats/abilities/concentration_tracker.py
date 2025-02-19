from src.events.observer import Emitter
from src.util.constants import EventType

class ConcentrationTracker(Emitter):
    def __init__(self):
        super().__init__()
        self._ability = None
        self._remaining_ticks = 0
    
    @property
    def concentrating(self):
        return self._ability is not None

    def set_concentration(self, ability, duration):
        if self._ability is not None:
            self.end_concentration()
        self._ability = ability
        self._remaining_ticks = duration
    
    def end_concentration(self):
        if self._ability is not None:
            self.emit(EventType.ABILITY_CONCENTRATION_ENDED, self._ability._uuid)
            self._ability = None
            self._remaining_ticks = 0

    def tick_timer(self):
        if self._remaining_ticks > 0:
            self._remaining_ticks -= 1
            if self._remaining_ticks <= 0:
                self.end_concentration()