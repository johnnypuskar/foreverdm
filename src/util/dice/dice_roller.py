import random

class DiceRoller:
    def __init__(self):
        pass
    
    def _roll_die(self, sides):
        return random.randint(1, sides)

    def roll_custom(self, amount, sides):
        return sum([self._roll_die(sides) for i in range(amount)])

    def roll_d20(self, advantage = False, disadvantage = False):
        # Return a normal roll if no advantage or disadvantage, or if both advantage and disadvantage.
        if not advantage != disadvantage:
            return self._roll_die(20)
        if advantage:
            return max(self._roll_die(20), self._roll_die(20))
        if disadvantage:
            return min(self._roll_die(20), self._roll_die(20))
    
    def roll_d12(self, amount = 1):
        return sum([self._roll_die(12) for i in range(amount)])
    
    def roll_d10(self, amount = 1):
        return sum([self._roll_die(10) for i in range(amount)])
    
    def roll_d8(self, amount = 1):
        return sum(self._roll_die(8) for _ in range(amount))
    
    def roll_d6(self, amount = 1):
        return sum(self._roll_die(6) for _ in range(amount))
    
    def roll_d4(self, amount = 1):
        return sum(self._roll_die(4) for _ in range(amount))