from src.combat.turns.agents.turn_agent import TurnAgent
from src.combat.turns.turn_actions import *

class TurnManager:
    def __init__(self, agents = []):
        self._agents = agents
    
    @property
    def agents(self):
        return self._agents
    
    def advance_state(self):
        """
        Advances the state of the TurnManager by having the agent at the top of the order make a turn action, or end their turn.
        """
        if len(self._agents) == 0:
            return
        turn_action = self._agents[0].get_turn_action()
        if isinstance(turn_action, TurnActionEndTurn):
            self._agents.append(self._agents.pop(0))
            self._agents[0].reset()
        return turn_action
    
    def sort_agents(self):
        """
        Sorts the agents in the TurnManager turn order by their initiative values.
        """
        self._agents.sort(key = lambda x: x.initiative, reverse = True)

    def add_agent(self, agent: TurnAgent):
        """
        Adds a TurnAgent to the list of agents in the TurnManager.
        Newly added agents will be placed at the end of the turn order.
        """
        self._agents.append(agent)
    
    def remove_agent(self, agent: TurnAgent):
        """
        Removes a TurnAgent from the list of agents in the TurnManager.
        """
        self._agents.remove(agent)
    
