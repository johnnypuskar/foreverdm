from src.stats.statblock import Statblock

class Token:
    def __init__(self, statblock = None, position = (-1, -1)):
        self._position = position

        self._can_action = True
        self._can_bonus_action = True
        self._can_free_interaction = True
        self._can_reaction = True


class TokenExtension(Token):
    def __init__(self, parent):
        super.__init__()
        self._parent = parent

    @property
    def parent(self):
        return self._parent