
class EventContext:
    def __init__(self, source):
        self._source = source
        self.proceed = True
    
    @property
    def source(self):
        return self._source

    def decompose(self):
        return [self._source]

class NumericRollEventContext(EventContext):
    def __init__(self, source, damage_string: str):
        EventContext.__init__(self, source)
        self.damage_string = damage_string
    
    def decompose(self):
        return [self._source, self.damage_string]

class RollEventContext(EventContext):
    def __init__(self, source, advantage: bool, disadvantage: bool, auto_succeed: bool, auto_fail: bool, bonus: int):
        EventContext.__init__(self, source)
        self.advantage = advantage
        self.disadvantage = disadvantage
        self.auto_succeed = auto_succeed
        self.auto_fail = auto_fail
        self.bonus = bonus
    
    def decompose(self):
        return [self._source, self.advantage, self.disadvantage, self.auto_succeed, self.auto_fail, self.bonus]

class TargetedEventContext(EventContext):
    def __init__(self, source, target):
        EventContext.__init__(self, source)
        self.target = target
    
    def decompose(self):
        return [self._source, self.target]

class RollResultEventContext(EventContext):
    def __init__(self, source, result: int, success: bool, critical_success: bool):
        EventContext.__init__(self, source)
        self.result = result
        self.success = success
        self.critical_success = critical_success
    
    def decompose(self):
        return [self._source, self.result, self.success, self.critical_success]

class TargetedRollResultEventContext(TargetedEventContext, RollResultEventContext):
    def __init__(self, source, target, result: int, success: bool, critical_success: bool):
        RollResultEventContext.__init__(self, source, result, success, critical_success)
        TargetedEventContext.__init__(self, source, target)
    
    def decompose(self):
        return [self._source, self.target, self.result, self.success, self.critical_success]

class AttackRollEventContext(TargetedEventContext, RollEventContext):
    def __init__(self, source, target, advantage: bool, disadvantage: bool, auto_succeed: bool, auto_fail: bool, bonus: int):
        RollEventContext.__init__(self, source, advantage, disadvantage, auto_succeed, auto_fail, bonus)
        TargetedEventContext.__init__(self, source, target)
    
    def decompose(self):
        return [self._source, self.target, self.advantage, self.disadvantage, self.auto_succeed, self.auto_fail, self.bonus]

class DamageRollContext(EventContext):
    def __init__(self, source, damage_type, die_list: list):
        EventContext.__init__(self, source)
        self.damage_type = damage_type
        self.die_list = die_list
    
    def decompose(self):
        return [self._source, self.die_list]

class DamageEventContext(EventContext):
    def __init__(self, source, amount: int, type: str):
        EventContext.__init__(self, source)
        self.amount = amount
        self.type = type
    
    def decompose(self):
        return [self._source, self.amount, self.type]