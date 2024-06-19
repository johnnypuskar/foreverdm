class TurnAction:
    def __init__(self, agent: object):
        pass

class TurnActionEndTurn(TurnAction):
    def __init__(self, agent: object):
        super().__init__(agent)

class TurnActionMove(TurnAction):
    def __init__(self, agent: object):
        super().__init__(agent)

class TurnActionAbility(TurnAction):
    def __init__(self, agent: object):
        super().__init__(agent)