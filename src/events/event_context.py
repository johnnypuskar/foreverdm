
class EventContext:
    def __init__(self, source):
        self._source = source
    
    @property
    def source(self):
        return self._source

class RollEventContext(EventContext):
    def __init__(self, source, advantage, disadvantage, auto_succeed, auto_fail, bonus):
        super().__init__(source)
        self.advantage = advantage
        self.disadvantage = disadvantage
        self.auto_succeed = auto_succeed
        self.auto_fail = auto_fail
        self.bonus = bonus