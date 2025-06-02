from server.backend.errors.error_index import Errors
from server.backend.instances.commands.move_location_command import MoveLocationCommand

class CommandFactory:
    @staticmethod
    def new(command_type, statblock_id, campaign_id, *args):
        commands = {
            MoveLocationCommand.TYPE: MoveLocationCommand
        }
        if command_type in commands:
            return commands[command_type](statblock_id, campaign_id, *args)
        raise Errors.InvalidCommand(command_type)