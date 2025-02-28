from src.util.dice.dice_roller import DiceRoller

class UserRoller(DiceRoller):
    def __init__(self, user_id):
        super().__init__()
        self._user_id = user_id
    
    def roll_d20(self, advantage = False, disadvantage = False):
        result = None
        while result is None or not isinstance(result, int):
            try:
                result = int(input("Enter d20 result: "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        return result