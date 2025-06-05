from server.backend.errors.error_index import Errors
from server.backend.instances.commands.move_location_command import MoveLocationCommand
from server.backend.instances.commands.move_token_command import MoveTokenCommand

class CommandFactory:
    @staticmethod
    def new(command_type, statblock_id, campaign_id, *args):
        commands = {
            MoveLocationCommand.TYPE: MoveLocationCommand,
            MoveTokenCommand.TYPE: MoveTokenCommand,
        }
        if command_type in commands:
            return commands[command_type](statblock_id, campaign_id, *args)
        raise Errors.InvalidCommand(command_type)