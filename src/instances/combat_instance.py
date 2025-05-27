from src.instances.instance import StatblockNotInInstanceError
from src.instances.turn_instance import TurnInstance, CommandNotOnTurnError
from src.util.return_status import ReturnStatus
from src.control.commands.combat_move_command import CombatMoveCommand
from src.control.commands.use_ability_command import UseAbilityCommand
from src.control.commands.end_turn_command import EndTurnCommand
from src.combat.map.map_navigation import NavigationHandler
from src.stats.handlers.ability_handler import AbilityHandler
from src.combat.map.map_token import Token

class CombatInstance(TurnInstance):
    def __init__(self, map):
        super().__init__()
        self.type = 'COMBAT'
        self._map = map
        self._nav = NavigationHandler(self._map)

    def add_statblock(self, statblock, owner_id, position = (0, 0, 0)):
        id = super().add_statblock(statblock, owner_id)
        self._map.add_token(Token(statblock, position, map = self._map))
        return id

    def initiate_combat(self):
        initiative_scores = {}
        for statblock_id in self._statblocks.keys():
            statblock = self.get_statblock(statblock_id)
            initiative_modifier = statblock.get_initiative_modifier()
            roll_result = statblock._dice_roller.roll_d20(initiative_modifier.advantage, initiative_modifier.disadvantage)
            initiative_scores[statblock_id] = roll_result + initiative_modifier.bonus
        self.order_turns(initiative_scores)

    def advance_turn_order(self):
        super().advance_turn_order()
        statblock = self.get_statblock(self._turn_order[self._current])
        statblock._speed.reset()

    def issue_command(self, statblock_id, command):
        try:
            super().issue_command(statblock_id, command)
        except StatblockNotInInstanceError:
            return ReturnStatus(False, "Given statblock is not in this instance.")
        except CommandNotOnTurnError:
            return ReturnStatus(False, "Can only issue commands on that statblock's turn.")
        
        if isinstance(command, EndTurnCommand):
            self.advance_turn_order()
            return ReturnStatus(True, "Turn ended.")

        statblock = self.get_statblock(statblock_id)
        token = None
        for map_token in self._map.get_tokens():
            if map_token._statblock == statblock:
                token = map_token
                break

        if isinstance(command, CombatMoveCommand):
            path = self._nav.get_path(token, token.get_position(), command.to_position)
            if path is None:
                return ReturnStatus(False, "No path to target.")
            
            # TODO: Move statblock along path one space at a time to allow for movement reactions

            token.set_position(command.to_position)
            statblock._speed.distance_moved += path.distance
            return ReturnStatus(True, f"Moved {path.distance}ft to {command.to_position}.")
        elif isinstance(command, UseAbilityCommand):
            handler = AbilityHandler(token)

            return_status = None
            for use in command.ability_uses:
                use.args = list(use.args)
                for i in range(len(use.args)):
                    if self.has_statblock(use.args[i]):
                        statblock = self.get_statblock(use.args[i])
                        for map_token in self._map.get_tokens():
                            if map_token._statblock == statblock:
                                use.args[i] = map_token
                                break
                return_status = handler.use_ability(use.name, *use.args)
                if not return_status.success:
                    break
            return return_status
                
