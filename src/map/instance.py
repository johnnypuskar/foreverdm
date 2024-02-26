from src.map.battlemap import Map
from src.map.movement import MovementCost
from src.map.token import Token
from src.map.navigation import NavAgent

class Instance:
    def __init__(self, starting_map = None):
        self.map = starting_map
        self.tokens = []

    def get_context(self):
        tokens_context = {}
        for token in self.tokens:
            tokens_context[token.statblock.name] = token.position
        
        interactables_context = {}
        for interactable in self.map.interactables:
            interactables_context[interactable.name] = interactable.position

        return f"TOKEN POSITIONS: {tokens_context} | INTERACTABLES: {interactables_context}"

    def add_token(self, token, position):
        if token in self.tokens:
            raise ValueError(f"Token {token} already exists within instance.")
        for existing_token in self.tokens:
            if existing_token.position == position:
                raise PositionOccupiedError(f"Position {position} is already occupied by token {existing_token}.")
        token.position = position
        self.tokens.append(token)
    
    def remove_token(self, token):
        if token not in self.tokens:
            raise ValueError(f"Token {token} does not exist within instance: {self.tokens}")
        self.tokens.remove(token)

    def add_map_prop(self, prop, position):
        self.map.add_prop(prop, position)
    
    def remove_map_prop(self, prop):
        self.map.remove_prop(prop)

    def load_map(self, new_map):
        self.map = new_map
    
    def move_token(self, token, new_position):
        if token not in self.tokens:
            raise ValueError(f"Token {token} does not exist within instance.")
        if not self.map.within_boundaries(new_position[0], new_position[1]):
            raise ValueError(f"Position {new_position} is not within map boundaries.")
        for existing_token in self.tokens:
            if existing_token.position == new_position:
                raise PositionOccupiedError(f"Position {new_position} is already occupied by token {existing_token}.")
        
        nav = NavAgent(token.speed, token.size)
        reachable, _, _ = nav.get_reachable_nodes(self.map, token.position)

        if new_position not in reachable:
            return False

        token.position = new_position
        token.speed -= reachable[new_position]

        return True
    
    def add_prop(self, prop, position):
        self.map.add_prop(prop, position)

class PositionOccupiedError(Exception):
    pass