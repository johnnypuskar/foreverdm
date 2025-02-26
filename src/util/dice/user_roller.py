from src.util.dice.dice_roller import DiceRoller

class UserRoller(DiceRoller):
    def __init__(self, user_id):
        super().__init__()
        self._user_id = user_id