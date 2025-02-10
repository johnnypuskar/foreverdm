class ResettableValue:
    def __init__(self, value, initial = None):
        self.value = value
        if initial is None:
            self._initial = value
        else:
            self._initial = initial

    @property
    def initial(self):
        return self._initial

    def add_capped(self, value):
        self.value = min(self.value + value, self._initial)

    def reset(self):
        self.value = self._initial

    def __str__(self):
        return f'{self.value}/{self._initial}'
    
    def __repr__(self):
        return f'{self.value}/{self._initial}'

    def __lt__(self, other):
        if isinstance(other, ResettableValue):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
    
    def __gt__(self, other):
        if isinstance(other, ResettableValue):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other

    def __le__(self, other):
        if isinstance(other, ResettableValue):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other

    def __ge__(self, other):
        if isinstance(other, ResettableValue):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other

    def __add__(self, other):
        if isinstance(other, ResettableValue):
            return ResettableValue(self.value + other.value, self._initial)
        elif isinstance(other, int):
            return ResettableValue(self.value + other, self._initial)

    def __radd__(self, other):
        if isinstance(other, ResettableValue):
            return self.__add__(other)
        elif isinstance(other, int):
            return other + self.value

    def __sub__(self, other):
        if isinstance(other, ResettableValue):
            return ResettableValue(self.value - other.value, self._initial)
        elif isinstance(other, int):
            return ResettableValue(self.value - other, self._initial)
    
    def __rsub__(self, other):
        if isinstance(other, ResettableValue):
            return ResettableValue(other.value - self.value, other._initial)
        elif isinstance(other, int):
            return other - self.value

class CappedValue:
    def __init__(self, max, value = None, initial = None):
        self._max = max
        self._value = 0 if value is None else value
        self._initial = 0 if initial is None else initial

    @property
    def value(self):
        return self._max - self._value

    @value.setter
    def value(self, new_value):
        self._value = self._max - new_value

    @property
    def max(self):
        return self._max

    @property
    def initial(self):
        return self._initial

    def reset(self):
        self._value = self._initial

    def __str__(self):
        return f'({self.value}/{self._max})'
    
    def __repr__(self):
        return f'({self.value}/{self._max})'

    def __lt__(self, other):
        if isinstance(other, CappedValue):
            return (self.max - self._value) < (other.max - other._value)
        elif isinstance(other, int):
            return (self.max - self._value) < other

    def __gt__(self, other):
        if isinstance(other, CappedValue):
            return (self.max - self._value) > (other.max - other._value)
        elif isinstance(other, int):
            return (self.max - self._value) > other

    def __le__(self, other):
        if isinstance(other, CappedValue):
            return (self.max - self._value) <= (other.max - other._value)
        elif isinstance(other, int):
            return (self.max - self._value) <= other

    def __ge__(self, other):
        if isinstance(other, CappedValue):
            return (self.max - self._value) >= (other.max - other._value)
        elif isinstance(other, int):
            return (self.max - self._value) >= other

    def __add__(self, other):
        if isinstance(other, CappedValue):
            return CappedValue(self._max, self._value + other._value, self._initial)
        elif isinstance(other, int):
            return CappedValue(self._max, self._value + other, self._initial)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, CappedValue):
            return CappedValue(self._max, self._value - other._value, self._initial)
        elif isinstance(other, int):
            return CappedValue(self.max, self._value - other, self._initial)

    def __rsub__(self, other):
        if isinstance(other, CappedValue):
            return CappedValue(other.max, other._value - self._value, other.initial)
        elif isinstance(other, int):
            return CappedValue(self.max, other - self._value, self._initial)

