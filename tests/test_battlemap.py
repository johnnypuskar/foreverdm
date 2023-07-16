import unittest
from src.map.battlemap import *
from src.map.navigation import *
from src.stats.statistics import Speed
import sys

class TestMap(unittest.TestCase):

    def setUp(self) -> None:
        sys.stdout.reconfigure(encoding='utf-8')
        return super().setUp()

    def test_setup(self):
        grid = Map(8, 6)
        # Testing correct dimension property assignment
        self.assertEqual(grid.width, 8)
        self.assertEqual(grid.height, 6)

        # Testing map grid created and at correct size
        self.assertIsNotNone(grid._grid)
        self.assertEqual(len(grid._grid), 6)
        self.assertEqual(len(grid._grid[0]), 8)
        
    def test_cover(self):
        grid = Map(20, 10)
        # Testing getting cover value
        self.assertEqual(grid.calculate_cover((3, 6), (5, 5)), 0)
        # Testing getting cover value vertically
        self.assertEqual(grid.calculate_cover((2, 2), (2, 8)), 0)
        # Testing getting cover value horizontally
        self.assertEqual(grid.calculate_cover((3, 4), (12, 4)), 0)

        # Adding walls to map (half cover walls and three-quarters-cover walls)
        for y in range(10):
            grid.set_tile(4, y, MapTile((4, y), wall_right = TileWall(cover = 1, passable = True)))
            grid.set_tile(5, y, MapTile((5, y), wall_left = TileWall(cover = 1, passable = True)))
            grid.set_tile(14, y, MapTile((14, y), wall_right = TileWall(cover = 2, passable = True)))
            grid.set_tile(15, y, MapTile((15, y), wall_left = TileWall(cover = 2, passable = True)))

        # Testing calculating half cover
        self.assertEqual(grid.calculate_cover((2, 2), (8, 4)), 1)
        self.assertEqual(grid.calculate_cover((2, 2), (7, 2)), 1)

        # Testing calculating three-quarters cover
        self.assertEqual(grid.calculate_cover((12, 6), (18, 4)), 2)
        self.assertEqual(grid.calculate_cover((12, 6), (17, 6)), 2)

        # Testing cumulative cover detection (takes highest)
        self.assertEqual(grid.calculate_cover((2, 6), (18, 4)), 2)
        self.assertEqual(grid.calculate_cover((2, 6), (17, 6)), 2)


    def test_load_file(self):
        # Load test map
        TEST_MAP_PATH = "C:/Users/johnn/Programming/Python/ForeverDM/ForeverDM/data/test_map.fdm"
        grid = Map.load_from_file(TEST_MAP_PATH)
        
        # Testing various known points for loaded properties
        self.assertFalse(grid.get_tile(3, 1).passable)
        self.assertEqual(grid.get_tile(2, 4).movement_cost.walking, 10)

        # Testing for obstacles obstructing cover across full map
        self.assertEqual(grid.calculate_cover((1, 1), (14, 12)), 3)

        # Testing for no obstructions over hole tiles
        self.assertEqual(grid.calculate_cover((1, 1), (1, 7)), 0)
        
        print(grid.text_visualization())
        print(grid.get_tile(7, 11).wall_bottom)

    def test_pathfinding(self):
        grid = Map.load_from_file("C:/Users/johnn/Programming/Python/ForeverDM/ForeverDM/data/test_map.fdm")


        graph = grid.calculate_navgraph()
        agent = NavAgent(Speed(30))
        reachable, paths = agent.get_reachable_nodes(graph, (3, 10))

        print("\n" + grid.text_visualization([node.position for node in reachable]))

        # Print out amount of reachable nodes
        print(f"Reachable nodes: {len(reachable)}")

        for node in reachable:
            print(f"Node {node.position} - {paths[node.position]}")


class TestTiles(unittest.TestCase):
    def test_map_tile(self):
        tile = MapTile(passable = False, movement_cost = MovementCost(10), prop = None)

        # Testing properties were assigned properly
        self.assertFalse(tile.passable)
        self.assertEqual(tile.movement_cost.walking, 10)
        self.assertEqual(tile.cover, 0)
        self.assertIsNone(tile.prop)

    def test_map_tile_prop(self):
        prop = MapProp(1, MovementCost(5), False)
        tile = MapTile(passable = True, movement_cost = MovementCost(10), prop = None)

        # Testing properties were assigned properly
        self.assertIsNone(tile.prop)
        self.assertTrue(tile.passable)
        self.assertEqual(tile.movement_cost.walking, 10)
        self.assertEqual(tile.cover, 0)

        # Adding prop to tile
        tile.prop = prop

        # Testing prop correctly modifies tile properties
        self.assertEqual(tile.prop, prop)
        self.assertFalse(tile.passable)
        self.assertEqual(tile.movement_cost.walking, 15)
        self.assertEqual(tile.cover, 1)

    def test_tile_wall(self):
        wall = TileWall(2, True, 5)

        # Testing propertes were assigned properly
        self.assertTrue(wall.passable)
        self.assertEqual(wall.cover, 2)
        self.assertEqual(wall.movement_penalty, 5)

    def test_tile_door(self):
        door = TileDoor(3, False, 5)
        
        # Testing properties were assigned properly
        self.assertFalse(door.passable)
        self.assertEqual(door.cover, 3)
        self.assertEqual(door.movement_penalty, 5)

        # Testing properties are updated correctly when door is opened
        door.interact()
        self.assertTrue(door.passable)
        self.assertEqual(door.cover, 0)
        self.assertEqual(door.movement_penalty, 5)


class TestMapProp(unittest.TestCase):
    def interact_1(self):
        return 10

    def interact_2(self):
        return 20

    def test_properties(self):
        prop1 = MapProp(2, 5, True, use_action=True, interaction=self.interact_1)
        prop2 = MapProp(3, 10, False, use_reaction=True, interaction=self.interact_2)
        
        # Testing properties were assigned properly
        self.assertEqual(prop1.cover, 2)
        self.assertEqual(prop1.movement_penalty, 5)
        self.assertTrue(prop1.passable)
        
        # Testing properties were assigned properly
        self.assertEqual(prop2.cover, 3)
        self.assertEqual(prop2.movement_penalty, 10)
        self.assertFalse(prop2.passable)

    def test_interaction(self):
        prop1 = MapProp(2, 5, True, use_action=True, interaction=self.interact_1)
        prop2 = MapProp(3, 10, False, use_reaction=True, interaction=self.interact_2)
        
        # Testing interaction functions are assigned and work properly
        self.assertEqual(prop1.interact(), 10)
        self.assertEqual(prop2.interact(), 20)