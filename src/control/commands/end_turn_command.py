from src.control.commands.controller_command import ControllerCommand

class EndTurnCommand(ControllerCommand):
    TITLE = "end_turn"
    
    def __init__(self):
        super().__init__(EndTurnCommand.TITLE)