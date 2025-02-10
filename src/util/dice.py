from __future__ import annotations
import random, re

class DiceRoller:
    def __init__(self):
        pass
    
    def _roll_die(sides):
        return random.randint(1, sides)

    @staticmethod
    def roll_custom(amount, sides):
        return sum([DiceRoller._roll_die(sides) for i in range(amount)])

    @staticmethod
    def roll_d20(advantage = False, disadvantage = False):
        # Return a normal roll if no advantage or disadvantage, or if both advantage and disadvantage.
        if not advantage != disadvantage:
            return DiceRoller._roll_die(20)
        if advantage:
            return max(DiceRoller._roll_die(20), DiceRoller._roll_die(20))
        if disadvantage:
            return min(DiceRoller._roll_die(20), DiceRoller._roll_die(20))
    
    @staticmethod
    def roll_d12(amount = 1):
        return sum([DiceRoller._roll_die(12) for i in range(amount)])
    
    @staticmethod
    def roll_d10(amount = 1):
        return sum([DiceRoller._roll_die(10) for i in range(amount)])
    
    @staticmethod
    def roll_d8(amount = 1):
        return sum(DiceRoller._roll_die(8) for _ in range(amount))
    
    @staticmethod
    def roll_d6(amount = 1):
        return sum(DiceRoller._roll_die(6) for _ in range(amount))
    
    @staticmethod
    def roll_d4(amount = 1):
        return sum(DiceRoller._roll_die(4) for _ in range(amount))

class DiceSum:
    def __init__(self, d4 = 0, d6 = 0, d8 = 0, d10 = 0, d12 = 0, modifier = 0):
        self._d4 = d4
        self._d6 = d6
        self._d8 = d8
        self._d10 = d10
        self._d12 = d12
        self._modifier = modifier
    
    def roll(self):
        return DiceRoller.roll_d4(self._d4) + DiceRoller.roll_d6(self._d6) + DiceRoller.roll_d8(self._d8) + DiceRoller.roll_d10(self._d10) + DiceRoller.roll_d12(self._d12) + self._modifier

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

    def roll(self, die_multiplier = 1):
        total = self.modifier
        for die in self._dice:
            total += DiceRoller.roll_custom(self._dice[die] * die_multiplier, int(die[1:]))
        return total
    
    def roll_from_list(self, die_list):
        return sum([die["result"] for die in die_list]) + self.modifier

    def roll_to_list(self, die_multiplier = 1):
        roll_results = []
        for die in self._dice:
            for i in range(self._dice[die] * die_multiplier):
                roll_results.append({"sides": int(die[1:]), "result": DiceRoller.roll_custom(1, int(die[1:]))})
        return roll_results

class DiceParser:
    def __init__(self):
        pass
    
    @staticmethod
    def parse_string(dice_string):
        # Split the dice string into individual dice substrings
        regex = r"(^\d+|[+-]\d+)(d\d+)?"
        matches = re.findall(regex, dice_string)

        matched_string = "".join([match[0] + match[1] for match in matches])

        if matched_string != dice_string:
            raise ValueError(f"Invalid dice string: {dice_string}")
        
        dice = DiceInstance()

        for match in matches:
            multiplier = 1
            if match[0] == "-":
                multiplier = -1
            
            amount = int(match[0][1:]) if match[0][0] == "+" else int(match[0])
            if len(match[1]) > 1:
                dice.add_dice(int(match[1][1:]), amount * multiplier)
            else:
                dice.modifier += amount * multiplier
        
        return dice