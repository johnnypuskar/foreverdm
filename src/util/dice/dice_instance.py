from __future__ import annotations

class DiceInstance:
    def __init__(self):
        self._dice = {}
        self.modifier = 0
    
    @property
    def has_dice(self):
        return len(self._dice) > 0

    def add_dice(self, sides: int, amount: int):
        if sides < 0:
            raise ValueError("Sides must be greater than 0.")
        if amount <= 0:
            return
        if sides in self._dice.keys():
            self._dice[sides] += amount
        else:
            self._dice["d" + str(sides)] = amount
    
    def merge(self, other: DiceInstance):
        for die in other._dice.keys():
            if die in self._dice.keys():
                self._dice[die] += other._dice[die]
            else:
                self._dice[die] = other._dice[die]
        self.modifier += other.modifier

    def roll(self, die_roller, die_multiplier = 1):
        total = self.modifier
        for die in self._dice:
            total += die_roller.roll_custom(self._dice[die] * die_multiplier, int(die[1:]))
        return total
    
    def roll_from_list(self, die_list):
        return sum([die["result"] for die in die_list]) + self.modifier

    def roll_to_list(self, die_roller, die_multiplier = 1):
        roll_results = []
        for die in self._dice:
            for i in range(self._dice[die] * die_multiplier):
                roll_results.append({"sides": int(die[1:]), "result": die_roller.roll_custom(1, int(die[1:]))})
        return roll_results