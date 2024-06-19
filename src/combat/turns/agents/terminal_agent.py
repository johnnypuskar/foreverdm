from src.combat.turns.agents.turn_agent import TurnAgent
from src.combat.turns.turn_actions import *

class TerminalTurnAgent(TurnAgent):
    def __init__(self, initiative: int):
        super().__init__(initiative)
    
    def get_turn_action(self):
        print("Please enter a command:")
        command = input()
        match command:
            case "end":
                return TurnActionEndTurn(self)
            case "move":
                return TurnActionMove(self)
            case "ability":
                return TurnActionAbility(self)
            case _: 
                print("Invalid command. Ending turn.")
        return TurnActionEndTurn(self)