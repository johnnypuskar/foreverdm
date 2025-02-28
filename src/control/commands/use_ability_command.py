from src.control.commands.controller_command import ControllerCommand

class UseAbilityCommand(ControllerCommand):
    TITLE = "use_ability"
    
    class AbilityUse:
        def __init__(self, name, *args):
            self.name = name
            self.args = args

    def __init__(self):
        super().__init__(UseAbilityCommand.TITLE)
        self.ability_uses = []
    
    def use_ability(self, name, *args):
        self.ability_uses.append(UseAbilityCommand.AbilityUse(name, *args))