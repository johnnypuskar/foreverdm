
class MovementCost():
    cost_types = ('walking', 'flying', 'swimming', 'climbing', 'burrowing')

    def __init__(self, walking = None, flying = None, swimming = None, climbing = None, burrowing = None):
        self._walking = walking
        self._flying = flying if flying is not None else walking
        self._swimming = swimming
        self._climbing = climbing
        self._burrowing = burrowing

    @property
    def walking(self):
        return self._walking
    
    @property
    def flying(self):
        return self._flying
    
    @property
    def swimming(self):
        return self._swimming
    
    @property
    def climbing(self):
        return self._climbing
    
    @property
    def burrowing(self):
        return self._burrowing
    
    @property
    def highest_cost(self):
        return max(filter(lambda v: v is not None, (self.walking, self.flying, self.swimming, self.climbing, self.burrowing)))

    @property
    def has_no_movement(self):
        return self._walking is None and self._flying is None and self._swimming is None and self._climbing is None and self._burrowing is None

    @staticmethod
    def from_minimum_costs(first, second):
        if isinstance(first, MovementCost) and isinstance(second, MovementCost):
            return MovementCost(
                min(filter(lambda v: v is not None, (first.walking, second.walking)), default=None),
                min(filter(lambda v: v is not None, (first.flying, second.flying)), default=None),
                min(filter(lambda v: v is not None, (first.swimming, second.swimming)), default=None),
                min(filter(lambda v: v is not None, (first.climbing, second.climbing)), default=None),
                min(filter(lambda v: v is not None, (first.burrowing, second.burrowing)), default=None)
            )
        else:
            raise TypeError("Unsupported operand type: can only add two MovementCost objects")
        
    def __str__(self):
        return f"MovementCost(walking={self.walking}, flying={self.flying}, swimming={self.swimming}, climbing={self.climbing}, burrowing={self.burrowing})"

    def __add__(self, other):
        if isinstance(other, MovementCost):
            return MovementCost(
                sum(filter(lambda v: v is not None, (self.walking, other.walking))) if not any(v is None for v in (self.walking, other.walking)) else None,
                sum(filter(lambda v: v is not None, (self.flying, other.flying))) if not any(v is None for v in (self.flying, other.flying)) else None,
                sum(filter(lambda v: v is not None, (self.swimming, other.swimming))) if not any(v is None for v in (self.swimming, other.swimming)) else None,
                sum(filter(lambda v: v is not None, (self.climbing, other.climbing))) if not any(v is None for v in (self.climbing, other.climbing)) else None,
                sum(filter(lambda v: v is not None, (self.burrowing, other.burrowing))) if not any(v is None for v in (self.burrowing, other.burrowing)) else None
            )
    
    def __mul__(self, other):
        if isinstance(other, int):
            return MovementCost(
                None if self._walking is None else self._walking * other,
                None if self._flying is None else self._flying * other,
                None if self._swimming is None else self._swimming * other,
                None if self._climbing is None else self._climbing * other,
                None if self._burrowing is None else self._burrowing * other
            )
        else:
            raise TypeError(f"Unsupported operand type {type(other)}: can only multiply a MovementCost object by an integer")

    def __radd__(self, other):
        if isinstance(other, MovementCost):
            return self.__add__(other)
        if isinstance(other, int):
            return MovementCost(
                None if self.walking is None else self.walking + other,
                None if self.flying is None else self.flying + other,
                None if self.swimming is None else self.swimming + other,
                None if self.climbing is None else self.climbing + other,
                None if self.burrowing is None else self.burrowing + other
            )
        else:
            raise TypeError(f"Unsupported operand type {type(other)}: can only add int or MovementCost to MovementCost object")
    
    def __lt__(self, other):
        if isinstance(other, MovementCost):
            return self.highest_cost < other.highest_cost
        else:
            return self.highest_cost < other
