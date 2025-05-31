from server.backend.database.util.data_storer import DataStorer

class TurnResources(DataStorer):
    def __init__(self):
        super().__init__()
        self._action = True
        self._bonus_action = True
        self._reaction = True
        self._free_object_interaction = True

        self.map_data_property("_action", "action")
        self.map_data_property("_bonus_action", "bonus_action")
        self.map_data_property("_reaction", "reaction")
        self.map_data_property("_free_object_interaction", "free_object_interaction")

    def reset(self):
        self._action = True
        self._bonus_action = True
        self._reaction = True
        self._free_object_interaction = True

    def make_copy(self):
        copy = TurnResources()
        copy._action = self._action
        copy._bonus_action = self._bonus_action
        copy._reaction = self._reaction
        copy._free_object_interaction = self._free_object_interaction
        return copy

    def can_use(self, use_time):
        if use_time.is_special:
            if use_time.is_action:
                return self._action
            elif use_time.is_bonus_action:
                return self._bonus_action
            elif use_time.is_reaction:
                return self._reaction
        else:
            return self._action
        return False  # Failsafe

    def use_from_use_time(self, use_time):
        if use_time.is_special:
            if use_time.is_action:
                return self.use_action()
            elif use_time.is_bonus_action:
                return self.use_bonus_action()
            elif use_time.is_reaction:
                return self.use_reaction()
        else:
            return self.use_action()
        return False  # Failsafe

    def use_action(self):
        if self._action:
            self._action = False
            return True
        return False

    def use_bonus_action(self):
        if self._bonus_action:
            self._bonus_action = False
            return True
        return False

    def use_reaction(self):
        if self._reaction:
            self._reaction = False
            return True
        return False    

    def use_free_object_interaction(self):
        if self._free_object_interaction:
            self._free_object_interaction = False
            return True
        return False