
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

    def reset(self):
        self.value = self._initial

    def __str__(self):
        return str(self.value) + ' / ' + str(self._initial)

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
            return ResettableValue(other.value - self.value, self._initial)
        elif isinstance(other, int):
            return other - self.value