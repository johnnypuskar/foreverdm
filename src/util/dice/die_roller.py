import random

class DiceRoller:
    def __init__(self):
        pass
    
    def _roll_die(sides):
        return random.randint(1, sides)

    def roll_custom(amount, sides):
        return sum([DiceRoller._roll_die(sides) for i in range(amount)])

    def roll_d20(advantage = False, disadvantage = False):
        # Return a normal roll if no advantage or disadvantage, or if both advantage and disadvantage.
        if not advantage != disadvantage:
            return DiceRoller._roll_die(20)
        if advantage:
            return max(DiceRoller._roll_die(20), DiceRoller._roll_die(20))
        if disadvantage:
            return min(DiceRoller._roll_die(20), DiceRoller._roll_die(20))
    
    def roll_d12(amount = 1):
        return sum([DiceRoller._roll_die(12) for i in range(amount)])
    
    def roll_d10(amount = 1):
        return sum([DiceRoller._roll_die(10) for i in range(amount)])
    
    def roll_d8(amount = 1):
        return sum(DiceRoller._roll_die(8) for _ in range(amount))
    
    def roll_d6(amount = 1):
        return sum(DiceRoller._roll_die(6) for _ in range(amount))
    
    def roll_d4(amount = 1):
        return sum(DiceRoller._roll_die(4) for _ in range(amount))