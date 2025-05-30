import os
import unittest
from src.combat.map.battlemap import *
from src.combat.map.navigation import *
from src.stats.statistics import Speed
import sys

class TestMap(unittest.TestCase):

    def setUp(self) -> None:
        sys.stdout.reconfigure(encoding='utf-8')

        test_dir = os.path.dirname(os.path.abspath(__file__))

        self.TEST_LEVEL_SIZE = os.path.join(test_dir, "levels\\size_test_level.fdm")
        self.TEST_LEVEL_TERRAIN = os.path.join(test_dir, "levels\\terrain_test_level.fdm")
        self.TEST_LEVEL_WATER = os.path.join(test_dir, "levels\\water_test_small.fdm")

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

    def test_update_max_size(self):
        grid = Map(5, 5)
        grid.calculate_tiles_max_size()

        # Testing that size is bounded by the edges of the map
        self.assertEqual(grid.get_tile(0, 0).max_token_size, Size.GARGANTUAN)
        self.assertEqual(grid.get_tile(1, 1).max_token_size, Size.GARGANTUAN)
        self.assertEqual(grid.get_tile(2, 2).max_token_size, Size.HUGE)
        self.assertEqual(grid.get_tile(3, 3).max_token_size, Size.LARGE)
        self.assertEqual(grid.get_tile(4, 4).max_token_size, Size.MEDIUM)

        self.assertEqual(grid.get_tile(0, 1).max_token_size, Size.GARGANTUAN)
        self.assertEqual(grid.get_tile(0, 2).max_token_size, Size.HUGE)
        self.assertEqual(grid.get_tile(0, 3).max_token_size, Size.LARGE)
        self.assertEqual(grid.get_tile(0, 4).max_token_size, Size.MEDIUM)

        self.assertEqual(grid.get_tile(1, 0).max_token_size, Size.GARGANTUAN)
        self.assertEqual(grid.get_tile(2, 0).max_token_size, Size.HUGE)
        self.assertEqual(grid.get_tile(3, 0).max_token_size, Size.LARGE)
        self.assertEqual(grid.get_tile(4, 0).max_token_size, Size.MEDIUM)
        
        # Placing a wall on the map
        grid.set_tile(1, 2, MapTile((1, 2), wall_right = TileWall(cover = 3, passable = False)))
        grid.set_tile(2, 2, MapTile((2, 2), wall_left = TileWall(cover = 3, passable = False)))
        grid.calculate_tiles_max_size()

        # Testing that size is bounded by horizontal walls
        self.assertEqual(grid.get_tile(0, 0).max_token_size, Size.LARGE)
        self.assertEqual(grid.get_tile(1, 1).max_token_size, Size.MEDIUM)
        self.assertEqual(grid.get_tile(2, 2).max_token_size, Size.HUGE)
        self.assertEqual(grid.get_tile(1, 2).max_token_size, Size.MEDIUM)
        self.assertEqual(grid.get_tile(2, 1).max_token_size, Size.HUGE)

        grid.set_tile(3, 4, MapTile((3, 4), wall_top = TileWall(cover = 3, passable = False)))
        grid.set_tile(3, 3, MapTile((3, 3), wall_bottom = TileWall(cover = 3, passable = False)))
        grid.calculate_tiles_max_size()

        # Testing that size is bounded by vertical walls
        self.assertEqual(grid.get_tile(2, 2).max_token_size, Size.LARGE)
        self.assertEqual(grid.get_tile(3, 3).max_token_size, Size.MEDIUM)

    def test_get_tiles_in_line(self):
        grid = Map(20, 20)

        # Testing getting tiles in a horizontal line
        expected = [(10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (15, 10)]
        result = grid.get_tiles_in_line((10, 10), (15, 10))
        self.assertListEqual(expected, result)

        # Testing getting tiles in a backwards horizontal line
        expected = [(10, 10), (9, 10), (8, 10), (7, 10), (6, 10), (5, 10)]
        result = grid.get_tiles_in_line((10, 10), (5, 10))
        self.assertListEqual(expected, result)

        # Testing getting tiles in a vertical line
        expected = [(10, 10), (10, 11), (10, 12), (10, 13), (10, 14), (10, 15)]
        result = grid.get_tiles_in_line((10, 10), (10, 15))
        self.assertListEqual(expected, result)

        # Testing getting tiles in a backwards vertical line
        expected = [(10, 10), (10, 9), (10, 8), (10, 7), (10, 6), (10, 5)]
        result = grid.get_tiles_in_line((10, 10), (10, 5))
        self.assertListEqual(expected, result)

        # Testing getting tiles in a 45 degree diagonal line in all four directions
        expected = [(10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15)]
        result = grid.get_tiles_in_line((10, 10), (15, 15))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (11, 9), (12, 8), (13, 7), (14, 6), (15, 5)]
        result = grid.get_tiles_in_line((10, 10), (15, 5))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (9, 11), (8, 12), (7, 13), (6, 14), (5, 15)]
        result = grid.get_tiles_in_line((10, 10), (5, 15))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5)]
        result = grid.get_tiles_in_line((10, 10), (5, 5))
        self.assertListEqual(expected, result)

        # Testing getting tiles in other non-45 degree diagonal lines
        expected = [(10, 10), (11, 11), (12, 11), (13, 12), (14, 13), (15, 13), (16, 14)]
        result = grid.get_tiles_in_line((10, 10), (16, 14))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (9, 10), (8, 9), (7, 9), (6, 9), (5, 9), (4, 8), (3, 8)]
        result = grid.get_tiles_in_line((10, 10), (3, 8))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (9, 11), (8, 12), (7, 13), (7, 14), (6, 15), (5, 16), (4, 17)]
        result = grid.get_tiles_in_line((10, 10), (4, 17))
        self.assertListEqual(expected, result)

        expected = [(10, 10), (10, 9), (10, 8), (11, 7), (11, 6), (11, 5), (11, 4), (12, 3), (12, 2), (12, 1)]
        result = grid.get_tiles_in_line((10, 10), (12, 1))
        self.assertListEqual(expected, result)

        # Testing that getting tiles in a line that goes off the map returns only the tiles on the map
        expected = [(18, 10), (19, 10)]
        result = grid.get_tiles_in_line((18, 10), (25, 10))
        self.assertListEqual(expected, result)

        expected = [(10, 18), (10, 19)]
        result = grid.get_tiles_in_line((10, 18), (10, 25))
        self.assertListEqual(expected, result)

        expected = [(18, 18), (19, 19)]
        result = grid.get_tiles_in_line((18, 18), (25, 25))
        self.assertListEqual(expected, result)

        expected = [(1, 1), (0, 0)]
        result = grid.get_tiles_in_line((1, 1), (-5, -5))
        self.assertListEqual(expected, result)

        expected = [(1, 10), (0, 10)]
        result = grid.get_tiles_in_line((1, 10), (-5, 10))
        self.assertListEqual(expected, result)

        expected = [(10, 1), (10, 0)]
        result = grid.get_tiles_in_line((10, 1), (10, -5))
        self.assertListEqual(expected, result)

        small_grid = Map(3, 3)

        expected = [(0, 1), (1, 1), (2, 1)]
        result = small_grid.get_tiles_in_line((-10, 1), (20, 1))
        self.assertListEqual(expected, result)

        expected = [(1, 0), (1, 1), (1, 2)]
        result = small_grid.get_tiles_in_line((1, -10), (1, 20))
        self.assertListEqual(expected, result)

        expected = [(0, 0), (1, 1), (2, 2)]
        result = small_grid.get_tiles_in_line((-10, -10), (20, 20))
        self.assertListEqual(expected, result)

    def test_load_file(self):
        # Load test map
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)
        
        # Testing various known points for loaded properties
        self.assertEqual(grid.width, 16)
        self.assertEqual(grid.height, 16)
        self.assertTrue(grid.get_tile(0, 0).solid)
        self.assertFalse(grid.get_tile(1, 1).solid)
        self.assertEqual(grid.get_tile(1, 1).movement_cost.walking, 5)
        self.assertEqual(grid.get_tile(10, 2).movement_cost.walking, 10)
        self.assertIsNone(grid.get_tile(13, 3).movement_cost.walking)

        # Testing for obstacles obstructing cover across full map
        self.assertEqual(grid.calculate_cover((1, 1), (14, 14)), 3)

        # Testing for no obstructions over hole tiles
        self.assertEqual(grid.calculate_cover((1, 1), (1, 7)), 0)


class TestNavigation(unittest.TestCase):

    def setUp(self) -> None:
        sys.stdout.reconfigure(encoding='utf-8')

        test_dir = os.path.dirname(os.path.abspath(__file__))

        self.TEST_LEVEL_SIZE = os.path.join(test_dir, "levels\\size_test_level.fdm")
        self.TEST_LEVEL_TERRAIN = os.path.join(test_dir, "levels\\terrain_test_level.fdm")
        self.TEST_LEVEL_WATER = os.path.join(test_dir, "levels\\water_test_small.fdm")

        return super().setUp()

    def test_speed(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)

        # Creating pathfinding agents of varying speeds
        slow_agent = NavAgent(Speed(10), Size.MEDIUM)
        agent = NavAgent(Speed(30), Size.MEDIUM)
        fast_agent = NavAgent(Speed(50), Size.MEDIUM)

        # Testing that slowest agent can only reach 2 additional tiles away
        reachable, _, _ = slow_agent.get_reachable_nodes(grid, (8, 1))

        for i in range(1, 4):
            self.assertIn((8, i), reachable.keys())
        self.assertNotIn((8, 4), reachable.keys())

        # Testing that normal agent can reach 6 additional tiles away
        reachable, _, _ = agent.get_reachable_nodes(grid, (8, 1))

        for i in range(1, 8):
            self.assertIn((8, i), reachable.keys())
        self.assertNotIn((8, 8), reachable.keys())

        # Testing that fast agent can reach 10 additional tiles away
        reachable, _, _ = fast_agent.get_reachable_nodes(grid, (8, 1))

        for i in range(1, 12):
            self.assertIn((8, i), reachable.keys())
        self.assertNotIn((8, 12), reachable.keys())
    
    def test_difficult_terrain(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)
        agent = NavAgent(Speed(10), Size.MEDIUM)

        # Testing that difficult terrain costs extra movement
        next_pos, turns, full_path = agent.get_movement_to(grid, (9, 5), (14, 5))
        self.assertEqual(turns, 4)

        # Testing that pathfinding can go around difficult terrain
        next_pos, turns, full_path = agent.get_movement_to(grid, (9, 2), (13, 2))
        self.assertIn((11, 1), full_path)
        self.assertEqual(turns, 2)
    
    def test_pits(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)
        agent = NavAgent(Speed(30), Size.MEDIUM)

        # Testing that pits are impassable
        reachable, paths, _ = agent.get_reachable_nodes(grid, (4, 8))
        self.assertListEqual([(4, 8), (5, 8)], list(reachable.keys()))
    
    def test_water(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)

        # Testing that water slows down non-swimmers
        agent = NavAgent(Speed(20), Size.MEDIUM)
        next_pos, turns, full_path = agent.get_movement_to(grid, (8, 14), (14, 14))

        self.assertEqual(turns, 3)
        self.assertEqual(10, next_pos[0])

        # Testing that swim speed allows faster movement through water
        swimmer_agent = NavAgent(Speed(20, 0, 10), Size.MEDIUM)
        next_pos, turns, full_path = swimmer_agent.get_movement_to(grid, (8, 14), (14, 14))

        self.assertEqual(turns, 2)
        self.assertEqual(10, next_pos[0])

        # Testing that creatures cannot move onto land if they have only a swim speed
        fish_agent = NavAgent(Speed(0, 0, 50), Size.TINY)
        reachable, _, _ = fish_agent.get_reachable_nodes(grid, (11, 11))

        TEST_POOL_TILES = [(11, 11), (10, 11), (11, 10), (11, 12), (12, 11), (10, 10), (10, 12), (12, 10), (11, 9), (11, 13), (12, 12), (13, 11), (10, 9), (9, 12), (10, 13), (12, 9), (11, 8), (11, 14), (13, 10), (14, 11), (9, 13), (10, 14), (12, 8), (13, 9), (14, 10), (9, 14), (13, 8), (14, 9), (14, 8)]
        self.assertListEqual(TEST_POOL_TILES, list(reachable.keys()))
    
    def test_maze(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)

        MAZE_START = (1, 1)
        MAZE_DEST = (4, 7)
        MAZE_SOLUTION = [(1, 1), (2, 1), (2, 2), (3, 2), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (3, 5), (4, 5), (5, 5), (5, 6), (6, 6), (6, 7), (5, 7)]

        # Tests pathfinding agent ability to traverse maze in expected path
        agent = NavAgent(Speed(100), Size.MEDIUM)
        reachable, paths, _ = agent.get_reachable_nodes(grid, MAZE_START)

        self.assertIn(MAZE_DEST, reachable.keys())
        self.assertIn(MAZE_DEST, paths.keys())
        self.assertListEqual(MAZE_SOLUTION, paths[MAZE_DEST])
    
    def test_size(self):
        grid = Map.load_from_file(self.TEST_LEVEL_SIZE)

        tiny_agent = NavAgent(Speed(150), Size.TINY)
        small_agent = NavAgent(Speed(150), Size.SMALL)
        medium_agent = NavAgent(Speed(150), Size.MEDIUM)
        large_agent = NavAgent(Speed(150), Size.LARGE)
        huge_agent = NavAgent(Speed(150), Size.HUGE)
        gargantuan_agent = NavAgent(Speed(150), Size.GARGANTUAN)

        # Testing that the gargantuan agent is stuck in the first area
        reachable, _, _ = gargantuan_agent.get_reachable_nodes(grid, (1, 1))
        GARGANTUAN_ACCESSIBLE = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (1, 3), (3, 1), (3, 2), (3, 3)]
        
        self.assertListEqual(GARGANTUAN_ACCESSIBLE, list(reachable.keys()))

        # Testing that the huge agent can move through to the second areas
        reachable, _, _ = huge_agent.get_reachable_nodes(grid, (1, 1))
        HUGE_ACCESSIBLE = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (1, 3), (3, 1), (3, 2), (3, 3), (2, 4), (1, 4), (3, 4), (4, 2), (4, 1), (4, 3), (4, 4), (1, 5), (5, 1), (1, 6), (6, 1), (1, 7), (7, 1), (2, 7), (1, 8), (2, 8), (8, 1), (1, 9), (3, 8), (3, 7), (9, 2), (8, 2), (9, 1), (1, 10), (4, 8), (4, 7), (9, 3), (8, 3), (10, 1), (10, 2), (10, 3), (1, 11), (11, 1), (11, 2), (11, 3)]
        
        self.assertListEqual(HUGE_ACCESSIBLE, list(reachable.keys()))

        # Testing that the large agent can move through to the third area
        reachable, _, _ = large_agent.get_reachable_nodes(grid, (1, 1))
        LARGE_ACCESSIBLE = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (1, 3), (3, 1), (3, 2), (3, 3), (2, 4), (1, 4), (3, 4), (4, 2), (4, 1), (4, 3), (4, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (2, 6), (1, 6), (6, 2), (6, 1), (2, 7), (1, 7), (7, 1), (7, 2), (1, 8), (2, 8), (3, 8), (3, 7), (8, 1), (8, 2), (2, 9), (1, 9), (3, 9), (4, 8), (4, 7), (4, 9), (9, 2), (9, 1), (9, 3), (8, 3), (2, 10), (1, 10), (5, 8), (5, 7), (5, 9), (8, 4), (9, 4), (10, 1), (10, 2), (10, 3), (10, 4), (1, 11), (2, 11), (6, 9), (11, 1), (11, 2), (11, 3), (11, 4), (10, 5), (1, 12), (2, 12), (7, 9), (10, 6), (12, 1), (12, 2), (12, 3), (12, 4), (8, 9), (10, 7), (9, 10), (8, 8), (9, 9), (8, 10), (9, 8), (10, 8), (9, 7), (8, 7), (9, 11), (8, 11), (10, 9), (10, 10), (10, 11), (9, 12), (7, 12), (8, 12), (7, 11), (10, 12), (11, 12), (11, 11), (6, 12), (6, 11), (5, 11), (5, 12), (4, 12), (4, 11)]
        
        self.assertListEqual(LARGE_ACCESSIBLE, list(reachable.keys()))

        # Testing that the medium agent can move through all movable spaces
        reachable, _, _ = medium_agent.get_reachable_nodes(grid, (1, 1))
        WALKABLE_TILES = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (1, 3), (3, 1), (3, 2), (3, 3), (2, 4), (1, 4), (3, 4), (4, 2), (4, 1), (4, 3), (4, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (2, 6), (1, 6), (3, 6), (4, 6), (5, 6), (6, 2), (6, 1), (6, 3), (6, 4), (6, 5), (6, 6), (2, 7), (1, 7), (3, 7), (7, 1), (7, 2), (7, 3), (1, 8), (2, 8), (3, 8), (4, 8), (4, 7), (8, 1), (8, 2), (8, 3), (2, 9), (1, 9), (3, 9), (4, 9), (5, 8), (5, 7), (5, 9), (9, 2), (9, 1), (9, 3), (8, 4), (9, 4), (2, 10), (1, 10), (3, 10), (4, 10), (5, 10), (6, 8), (6, 7), (6, 9), (6, 10), (9, 5), (8, 5), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (1, 11), (2, 11), (3, 11), (7, 10), (7, 9), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (10, 6), (1, 12), (2, 12), (3, 12), (8, 10), (8, 9), (11, 7), (10, 7), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (2, 13), (1, 13), (3, 13), (9, 10), (8, 8), (9, 9), (9, 8), (9, 11), (8, 11), (10, 8), (11, 8), (9, 7), (13, 1), (13, 2), (13, 3), (13, 4), (13, 5), (8, 7), (9, 12), (7, 12), (8, 12), (7, 11), (10, 9), (10, 10), (10, 11), (10, 12), (11, 9), (12, 8), (6, 12), (6, 11), (7, 13), (8, 13), (6, 13), (9, 13), (10, 13), (11, 10), (11, 11), (11, 12), (11, 13), (13, 8), (5, 11), (5, 12), (5, 13), (12, 12), (12, 11), (12, 13), (14, 8), (13, 7), (14, 7), (13, 9), (14, 9), (4, 12), (4, 11), (4, 13), (13, 12), (13, 10), (14, 10), (15, 8), (15, 7), (15, 9), (15, 10), (13, 11), (14, 11), (13, 13), (14, 13), (14, 12), (15, 11), (16, 7), (16, 6), (15, 6), (16, 8), (16, 9), (16, 10), (16, 11), (15, 12), (15, 13), (15, 5), (16, 5), (16, 12), (17, 7), (17, 6), (17, 5), (17, 8), (17, 9), (17, 10), (17, 11), (17, 12), (16, 13), (17, 13), (18, 7), (18, 6), (18, 5), (18, 8), (18, 9), (18, 10), (18, 11), (18, 12), (15, 4), (16, 4), (17, 4), (18, 4), (16, 3), (15, 3), (17, 3), (18, 3), (16, 2), (15, 2), (17, 2), (18, 2), (15, 1), (16, 1), (17, 1), (18, 1)]

        self.assertListEqual(WALKABLE_TILES, list(reachable.keys()))
        
        # Testing that the small and tiny agents can also reach the same spaces
        reachable, _, _ = small_agent.get_reachable_nodes(grid, (1, 1))
        self.assertListEqual(WALKABLE_TILES, list(reachable.keys()))

        reachable, _, _ = tiny_agent.get_reachable_nodes(grid, (1, 1))
        self.assertListEqual(WALKABLE_TILES, list(reachable.keys()))

    def test_directed_push(self):
        grid = Map.load_from_file(self.TEST_LEVEL_TERRAIN)
        agent = NavAgent(Speed(15), Size.MEDIUM)

        # Testing that the directed push works horizontally, vertically, and at an angle.
        expected = [(3, 10), (4, 10), (5, 10)]
        result = agent.get_directed_push_to(grid, (2, 10), (15, 10), 15)
        self.assertListEqual(expected, result)

        expected = [(8, 5), (8, 6), (8, 7)]
        result = agent.get_directed_push_to(grid, (8, 4), (8, 15), 15)
        self.assertListEqual(expected, result)

        expected = [(4, 10), (5, 9), (6, 8)]
        result = agent.get_directed_push_to(grid, (5, 11), (15, 1), 15)

        # Testing that the directed push goes different distances based on max_distance
        expected = [(2, 8)]
        result = agent.get_directed_push_to(grid, (1, 8), (15, 8), 5)
        self.assertListEqual(expected, result)

        expected = [(2, 8), (3, 8)]
        result = agent.get_directed_push_to(grid, (1, 8), (15, 8), 10)
        self.assertListEqual(expected, result)

        expected = [(2, 8), (3, 8), (4, 8)]
        result = agent.get_directed_push_to(grid, (1, 8), (15, 8), 15)
        self.assertListEqual(expected, result)

        expected = [(2, 8), (3, 8), (4, 8), (5, 8)]
        result = agent.get_directed_push_to(grid, (1, 8), (15, 8), 20)
        self.assertListEqual(expected, result)

        # Testing that the directed push stops at obstacle tiles
        expected = [(8, 11)]
        for i in range(5, 30, 5):
            result = agent.get_directed_push_to(grid, (9, 11), (1, 11), i)
            self.assertListEqual(expected, result)
        
        # Testing that the directed push stops at walls
        expected = [(8, 8)]
        for i in range(5, 30, 5):
            result = agent.get_directed_push_to(grid, (9, 9), (1, 1), i)
            self.assertListEqual(expected, result)
        
        # Testing that the directed push does not stop at pits
        expected = [(2, 9), (3, 9), (4, 9)]
        result = agent.get_directed_push_to(grid, (1, 9), (15, 9), 15)
        self.assertListEqual(expected, result)

        expected = [(2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9)]
        result = agent.get_directed_push_to(grid, (1, 9), (15, 9), 30)
        self.assertListEqual(expected, result)

        # Testing that the directed push does not care about difficult terrain
        expected = [(10, 4), (11, 4), (12, 4), (13, 4)]
        result = agent.get_directed_push_to(grid, (9, 4), (15, 4), 20)
        self.assertListEqual(expected, result)

        # Testing that the directed push does not care about water, pits, and stops at obstacles all in one
        expected = [(14, 3), (14, 4), (14, 5), (14, 6), (14, 7), (14, 8), (14, 9), (14, 10), (14, 11), (14, 12), (14, 13), (14, 14)]
        result = agent.get_directed_push_to(grid, (14, 2), (14, 15), 200)

        # Testing that the directed push stops at the edge of the map
        empty_grid = Map(5, 5)

        expected = [(3, 1), (2, 1), (1, 1), (0, 1)]
        result = agent.get_directed_push_to(empty_grid, (4, 1), (0, 1), 40)
        self.assertListEqual(expected, result)

class TestTiles(unittest.TestCase):
    def test_map_tile(self):
        tile = MapTile(movement_cost = MovementCost(10), prop = None)

        # Testing properties were assigned properly
        self.assertEqual(tile.movement_cost.walking, 10)
        self.assertEqual(tile.cover, 0)
        self.assertIsNone(tile.prop)

    def test_map_tile_prop(self):
        prop = MapProp("Rubble", "A pile of rubble", 1, MovementCost(5), True)
        tile = MapTile(movement_cost = MovementCost(10), prop = None)

        # Testing properties were assigned properly
        self.assertIsNone(tile.prop)
        self.assertEqual(tile.movement_cost.walking, 10)
        self.assertEqual(tile.cover, 0)

        # Adding prop to tile
        tile.prop = prop

        # Testing prop correctly modifies tile properties
        self.assertEqual(tile.prop, prop)
        self.assertEqual(tile.movement_cost.walking, 15)
        self.assertEqual(tile.cover, 1)

    def test_tile_wall(self):
        wall = TileWall(2, True, 5)

        # Testing propertes were assigned properly
        self.assertTrue(wall.passable)
        self.assertEqual(wall.cover, 2)
        self.assertEqual(wall.movement_penalty, 5)

    def test_tile_door(self):
        door = TileDoor("Jail Cell Door", "A locked cell bar door. Closed.", 2, False, MovementCost(5))
        
        # Testing properties were assigned properly
        self.assertEqual(door.name, "Jail Cell Door")
        self.assertEqual(door.description, "A locked cell bar door. Closed.")
        self.assertFalse(door.passable)
        self.assertEqual(door.cover, 2)
        self.assertEqual(door.movement_penalty.walking, 5)

        # Testing properties are updated correctly when door is opened
        door.update("An unlocked cell bar door. Opened.", True)
        self.assertTrue(door.passable)
        self.assertEqual(door.cover, 0)
        self.assertEqual(door.movement_penalty.walking, 5)


class TestMapProp(unittest.TestCase):

    def test_properties(self):
        prop1 = MapProp("Box", "A large wooden box", 1, MovementCost(5), True)
        prop2 = MapProp("Statue", "A massive marble statue", 2, MovementCost(30), False)
        
        # Testing properties were assigned properly
        self.assertEqual(prop1.name, "Box")
        self.assertEqual(prop1.description, "A large wooden box")
        self.assertEqual(prop1.cover, 1)
        self.assertEqual(prop1.movement_penalty.walking, 5)
        self.assertTrue(prop1.passable)
        
        # Testing properties were assigned properly
        self.assertEqual(prop2.name, "Statue")
        self.assertEqual(prop2.description, "A massive marble statue")
        self.assertEqual(prop2.cover, 2)
        self.assertEqual(prop2.movement_penalty.walking, 30)
        self.assertFalse(prop2.passable)

    def test_interaction(self):
        prop1 = MapProp("Box", "A large wooden box", 1, MovementCost(5), True)
        
        # Testing interaction function updates values properly
        prop1.update("The shattered remains of a large wooden box", 0, MovementCost(0))
        self.assertEqual(prop1.description, "The shattered remains of a large wooden box")
        self.assertEqual(prop1.cover, 0)
        self.assertEqual(prop1.movement_penalty.walking, 0)
        self.assertTrue(prop1.passable)

        # Testing interaction function updates description but not values when they are not provided
        prop1.update("The shattered remains of a large wooden box stacked neatly in a pile")
        self.assertEqual(prop1.description, "The shattered remains of a large wooden box stacked neatly in a pile")
        self.assertEqual(prop1.cover, 0)
        self.assertEqual(prop1.movement_penalty.walking, 0)
        self.assertTrue(prop1.passable)