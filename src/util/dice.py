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

class DiceParser:
    def __init__(self):
        pass
    
    @staticmethod
    def parse_string(dice_string):
        just_numbers = r"(\d+)"
        check_pattern = r"^(\d*d\d+)([\+\-](\d*d\d+))*([\+\-]\d+)*$"
        groups_pattern = r"([\+\-]?(\d+d\d+|\d+))"
        if not re.match(check_pattern, dice_string):
            if re.match(just_numbers, dice_string):
                return {"MOD": int(dice_string)}
            raise ValueError(f"Invalid dice string: {dice_string}")
        
        return_table = {"MOD": 0}

        groups = re.findall(groups_pattern, dice_string)

        for group in groups:
            multiplier = 1
            if group[0] != group[1] and group[1][0] == '-':
                multiplier = -1
            dice_roll = group[0]

            if "d" in dice_roll:
                amount, sides = dice_roll.split("d")
                if amount == "":
                    amount = 1
                else:
                    amount = int(amount)
                sides = int(sides)
                return_table[sides] = amount * multiplier
            else:
                return_table["MOD"] += int(dice_roll) * multiplier
        
        return return_table

                
        
    