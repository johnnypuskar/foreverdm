from src.util.combat_instance_viewer import CombatInstanceViewer
from src.instances.combat_instance import CombatInstance
from src.combat.map.map import Map
from src.control.controller import Controller
from src.stats.statblock import Statblock
from src.combat.map.map_token import Token
from src.util.dice.user_roller import UserRoller
from src.stats.movement.speed import Speed

import asyncio
import random

from src.control.commands.combat_move_command import CombatMoveCommand
from src.control.commands.end_turn_command import EndTurnCommand
from src.control.commands.use_ability_command import UseAbilityCommand

from src.stats.abilities.default_abilities import MeleeAttackAbility, DashAbility
from src.stats.items.weapon_item import WeaponItem

async def main():
    player1 = Controller()
    player1_statblock = Statblock("Player 1", speed = Speed(30), dice_roller = UserRoller("ABC"))
    player1.statblock = player1_statblock

    player2 = Controller()
    player2_statblock = Statblock("Player 2", speed = Speed(30, 30), dice_roller = UserRoller("123"))
    player2.statblock = player2_statblock


    player1_statblock._abilities.add(MeleeAttackAbility())
    player1_statblock._abilities.add(DashAbility())

    sword = WeaponItem("Longsword", "", 3, 0.25, ["weapon_versatile", "martial_weapon", "melee_weapon"], melee_damage = "1d8 slashing")
    player1_statblock._inventory.main_hand = sword

    player2_statblock._abilities.add(MeleeAttackAbility())
    player2_statblock._abilities.add(DashAbility())

    battlemap = Map(10, 10, 4)

    for tile in battlemap.get_all_tiles():
        tile._max_depth = -3
        if tile.x >= 7:
            tile._height = 2
            if tile.x == 7:
                for h in range(0, 2):
                    tile._wall_left.set_passable(False, h)

    game = CombatInstance(battlemap)

    player1_ID = game.add_statblock(player1_statblock, "ABC", (3, 3, 0))
    player2_ID = game.add_statblock(player2_statblock, "123", (5, 2, 0))
    viewer = CombatInstanceViewer()

    game.initiate_combat()

    viewer.set_instance(game)
    viewer.start_background_updates()


    while True:
        print("[== New Turn ==]")
        current_ID = game._turn_order[game._current]
        command = ""
        while command != "end":
            command_input = await asyncio.to_thread(input, "Command (end, move, ability): ")
            command, *args = command_input.split()
            print("Press Next to continue.")
            if command == "move":
                coords = list(map(int, args))
                x = coords[0]
                y = coords[1]
                height = 0 if len(coords) <= 2 else coords[2]
                print(game.issue_command(current_ID, CombatMoveCommand((x, y, height))))
                print("Total Moved:", game.get_statblock(current_ID).get_speed().distance_moved)
            elif command == "ability":
                name, *args = args
                ability_command = UseAbilityCommand()
                for i in range(len(args)):
                    if args[i] == "player1":
                        args[i] = player1_ID
                    elif args[i] == "player2":
                        args[i] = player2_ID
                ability_command.use_ability(name, *args)
                print(game.issue_command(current_ID, ability_command))
        print(game.issue_command(current_ID, EndTurnCommand()))
        await asyncio.sleep(0.1)

# asyncio.run(main())

test = Statblock("Test", "abc", speed = Speed(30, 45))
data = test.export_data()
print(data)

test2 = Statblock("", "")
test2.import_data(data)
print(test2.export_data())
pass