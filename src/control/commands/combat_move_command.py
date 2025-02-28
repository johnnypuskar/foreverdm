from src.control.commands.controller_command import ControllerCommand

class CombatMoveCommand(ControllerCommand):
    TITLE = "move"

    def __init__(self, to_position):
        super().__init__(CombatMoveCommand.TITLE)
        self.to_position = to_position