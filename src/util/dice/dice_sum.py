class DiceSum:
    def __init__(self, d4 = 0, d6 = 0, d8 = 0, d10 = 0, d12 = 0, modifier = 0):
        self._d4 = d4
        self._d6 = d6
        self._d8 = d8
        self._d10 = d10
        self._d12 = d12
        self._modifier = modifier
    
    def roll(self, die_roller):
        return die_roller.roll_d4(self._d4) + die_roller.roll_d6(self._d6) + die_roller.roll_d8(self._d8) + die_roller.roll_d10(self._d10) + die_roller.roll_d12(self._d12) + self._modifier