import re
from src.util.dice.dice_instance import DiceInstance

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