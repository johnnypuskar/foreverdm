from src.instances.instance import Instance
from src.util.return_status import ReturnStatus

class TurnInstance(Instance):
    def __init__(self):
        super().__init__()
        self._turn_order = []
        self._current = 0

    def order_turns(self, scores: dict):
        """
        Orders the instance controllers based on the scores provided, highest to lowest.

        param scores: dict[uuid, int] - The scores to order the controllers by, with a statblock ID as the key and the score as the value.
        returns: None
        """
        self._turn_order = list(self._statblocks.keys())
        self._turn_order.sort(key=lambda c: scores[c], reverse=True)
        self._current = 0
    
    def issue_command(self, statblock_id, command):
        """Issues a command to a statblock."""
        super().issue_command(statblock_id, command)
        if self._turn_order[self._current] != statblock_id:
            raise CommandNotOnTurnError("Can only issue commands on that statblock's turn.")

    def advance_turn_order(self):
        """Advances the turn order to the next controller."""
        # TODO: Trigger end of turn logic for Statblock

        self._current = (self._current + 1) % len(self._statblocks)

        # TODO: Trigger start of turn logic for Statblock
        next_statblock = self.get_statblock(self._turn_order[self._current])
        next_statblock.tick()

    def reset_turn_order(self):
        """Resets the turn order to the beginning."""
        self._current = 0

class CommandNotOnTurnError(Exception):
    pass