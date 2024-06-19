from src.combat.turns.turn_actions import *

class TurnAgent:
    def __init__(self, initiative: int):
        self._initiative = initiative
    
    @property
    def initiative(self):
        return self._initiative
    
    def reset(self):
        pass

    def get_turn_action(self):
        return TurnActionEndTurn(self)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"TurnAgent(initiative = {self.initiative})"