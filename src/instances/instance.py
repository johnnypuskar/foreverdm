
class Instance:

    def __init__(self):
        self._statblocks = {}

    def add_statblock(self, statblock):
        self._statblocks[statblock.id] = statblock
        return statblock.id
    
    def remove_statblock(self, statblock_id):
        del self._statblocks[statblock_id]

    def get_statblock(self, statblock_id):
        return self._statblocks[statblock_id]

    def has_statblock(self, statblock_id):
        return statblock_id in self._statblocks.keys()

    def issue_command(self, statblock_id, command):
        if not self.has_statblock(statblock_id):
            raise StatblockNotInInstanceError()

class StatblockNotInInstanceError(Exception):
    pass