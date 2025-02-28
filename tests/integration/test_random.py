import unittest
from unittest.mock import patch

from src.control.commands.combat_move_command import CombatMoveCommand
from src.stats.size import Size
from src.combat.map.map_navigation import NavigationHandler
from src.combat.map.map_token import Token
from src.stats.statblock import Statblock
# from tests.util.map_viewer import MapViewer
from src.stats.effects.effect import Effect
from src.events.observer import Observer
from src.util.lua_manager import LuaManager
from src.combat.map.map import Map
from src.combat.map.map_utils import MapUtils
from src.combat.map.map_object import MapObject
from src.combat.map.map_tile_wall import MapTileWall
from src.stats.abilities.ability import Ability

class TestRandom(unittest.TestCase):
    def test_lua_reference(self):
        lua = LuaManager()

        class ObserverPrinter(Observer):
            def signal(self, event, *data):
                name, value = data
                print(name, value)
        observer = ObserverPrinter()

        # lua.connect(observer)
        print()

        lua.execute('''
        a = 10
        b = 20
        
        name = "Tim"

        function test(x, b)
            if b then
                name = x
            else
                name = "Mystery"
            end
        end
        ''')
        lua.execute('test("Tom", true)')
        lua.execute('test("Tombuktoo", false)')
        lua._lua.globals()["outer"] = 100
        lua.execute("use_time = 100")
        lua.execute('''
        for k,v in pairs(_ENV) do
            print(k)
        end
        ''')
    
    def test_other_lua_reference(self):
        script = '''
        value = 0

        function test_set(x)
            value = x
        end

        function test_modify()
            value.value = value.value + 5
        end

        function test_get()
            return value
        end
        '''
        class TestObject:
            def __init__(self, value = 0):
                self.value = value

        lua1 = LuaManager()
        lua1.execute(script)
        o = TestObject(5)

        lua1.run("test_set", o)
        self.assertEqual(lua1.run("test_get").value, 5)
        lua1.run("test_modify")
        self.assertEqual(lua1.run("test_get").value, 10)

        other_o = lua1.run("test_get")
        
        lua2 = LuaManager()
        lua2.execute(script)
        lua2.run("test_set", other_o)
        self.assertEqual(lua2.run("test_get").value, 10)
        lua2.run("test_modify")
        self.assertEqual(lua2.run("test_get").value, 15)

    def test_map_stuff(self):
        map = Map(10, 10)
        utils = MapUtils(map)

        for x, y, direction in utils.get_wall_points_in_line((0, 0), (12, 2)):
            print(f"({x}, {y}) {direction}")
    
    def test_map_object(self):
        door_script = '''
        is_open = false

        function open(password)
            if password == "gamer" then
                object.cover = 0
                object.passable = true
                return true
            end
            return false
        end
        '''
        door = MapTileWall(3, False, 2, script = door_script)
        key = MapObject("Key", script = '''
        function open()
            object.cover = 0
            object.passable = true
        end
                        
        function examine()
            return "A key"
        end
        ''')

        print(door.open(), door.cover, door.passable)
        door.apply(key)
        print(door.open("gamer"), door.cover, door.passable)
        print(key.examine())
        # print(door.examine())
        print(door._globals)
    
    def test_ability_redo(self):
        ability = Ability("test_ability", '''
            function run(target)
                return target * -1
            end
        ''')
        ability.initialize({})
        print(ability.run(15))
    
    def test_effect_redo(self):
        effect = Effect("test_effect", '''
            thingy = 1
            value = "hello"
            dir = {
                gaming = "gamer",
                wining = "winner"
            }
            arr = {1, 2, 3}
        ''')
    
    def test_map_moving(self):
        statblock = Statblock("Player")
        token = Token(statblock, (0, 0, 0))
        map = Map(10, 10)
        nav = NavigationHandler(map)
        map.add_token(token)

        other_statblock = Statblock("Biggo", size = Size.LARGE)
        other = Token(other_statblock, (2, 3, 0))
        map.add_token(other)

        paths = nav.get_all_paths(token, token.get_position())
        print(paths)
        # MapViewer.view_map_with_highlights(map, list(paths.keys()))
        # MapViewer.refresh_loop()
    
    def test_commands(self):
        cmd = CombatMoveCommand((0, 0, 0))
        print(cmd.to_position)