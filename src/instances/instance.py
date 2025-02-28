from uuid import uuid4

class Instance:

    class StatblockData:
        def __init__(self, statblock, owner_id):
            self.statblock = statblock
            self.owner_id = owner_id

    def __init__(self):
        self._statblocks = {}

    def add_statblock(self, statblock, owner_id):
        statblock_id = str(uuid4())
        self._statblocks[statblock_id] = Instance.StatblockData(statblock, owner_id)
        return statblock_id
    
    def remove_statblock(self, statblock_id):
        del self._statblocks[statblock_id]

    def get_statblock(self, statblock_id):
        return self._statblocks[statblock_id].statblock

    def has_statblock(self, statblock_id):
        return statblock_id in self._statblocks.keys()

    def owns_statblock(self, statblock_id, owner_id):
        return self._statblocks[statblock_id].owner_id == owner_id

    def issue_command(self, statblock_id, command):
        if not self.has_statblock(statblock_id):
            raise StatblockNotInInstanceError()

class StatblockNotInInstanceError(Exception):
    pass