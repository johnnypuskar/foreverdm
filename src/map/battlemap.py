import math
import json
from abc import ABC, abstractmethod
from typing import List, Tuple
from src.map.pathfind import NavGraph

class Map:

    MAP_VERSION = 0.1

    def __init__(self, width: int, height: int):
        if width < 1 or height < 1:
            raise ValueError("Width and height of map must be positive integers. Cannot create map of size (" + str(width) + ", " + str(height) + ")")
        self._width = width
        self._height = height
        
        self._navgraph = None
        self._cover_map = {}

        self._grid = []
        for y in range(self._height):
            self._grid.append([])
            for x in range(self._width):
                self._grid[y].append(MapTile((x, y)))
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    def get_tile(self, x, y):
        return self._grid[int(y)][int(x)]
    
    def set_tile(self, coordinates: Tuple[int, int], tile):
        self._grid[int(coordinates[1])][int(coordinates[0])] = tile
    
    def set_tile(self, x: int, y: int, tile):
        self._grid[int(y)][int(x)] = tile

    def calculate_cover(self, attacking, defending):
        # get_integer_points(start, end) - determines the points which would potentially overlap walls
        def get_integer_points(start, end):
            # Calculate the slope of the line
            if end[0] - start[0] != 0:
                m = (end[1] - start[1]) / (end[0] - start[0])
            else:
                m = float('inf')
                return set()
    
            # Calculate the y-intercept of the line
            c = start[1] - m * start[0]
    
            points = set()
            
            # Iterate over each integer x value
            for x in range(math.ceil(min(start[0], end[0])), math.floor(max(start[0], end[0])) + 1):
                # Calculate the corresponding y value and add the point
                if not math.isinf(m):
                    y = m * x + c
                    # Check if the point is not on an integer y
                    if not math.isclose(y, round(y), abs_tol=1e-10):
                        points.add((x, math.floor(y) + 0.5))
               
            # Iterate over each integer y value
            for y in range(math.ceil(min(start[1], end[1])), math.floor(max(start[1], end[1])) + 1):
                # Calculate the corresponding x value and add the point
                if m != 0:
                    x = (y - c) / m
                    # Check if the point is not on an integer x
                    if not math.isclose(x, round(x), abs_tol=1e-10):
                        # Add the point with the y value snapped to the nearest 0.5
                        points.add((math.floor(x) + 0.5, y))

            return points
        
        # Create empty set for all walls that must be considered for cover
        wall_points = set() #get_integer_points((attacking[0] + 0.5, attacking[1] + 0.5), (defending[0] + 0.5, defending[1] + 0.5))

        # Set attacking point to be coorindate point of corner closest to defending space
        if defending[0] > attacking[0]:
            attacking = (attacking[0] + 1, attacking[1])
        if defending[1] > attacking[1]:
            attacking = (attacking[0], attacking[1] + 1)
        
        # Add walls directly adjacent to defending space that face attacking space to set
        if abs(attacking[0] - defending[0] + 0.5) > 0.5:
            wall_points.add((defending[0] + 0.5 + (0.5 * math.copysign(1, attacking[0] - defending[0])), defending[1] + 0.5))
        if abs(attacking[1] - defending[1] + 0.5) > 0.5:
            wall_points.add((defending[0] + 0.5, defending[1] + 0.5 + (0.5 * math.copysign(1, attacking[1] - defending[1]))))
        
        # Populate wall_points set with all points from all four defending space corners
        for defending_point in [defending, (defending[0] + 1, defending[1]), (defending[0], defending[1] + 1), (defending[0] + 1, defending[1] + 1)]:
            wall_points.update(get_integer_points(attacking, defending_point))
        
        highest_cover = 0

        for wall_point in wall_points:
            if wall_point[0] == math.floor(wall_point[0]):
                # This wall is between two tiles horizontally adjacent
                left_wall = self.get_tile(wall_point[0], math.floor(wall_point[1])).wall_left
                if left_wall is not None:
                    highest_cover = max(highest_cover, left_wall.cover)
                if wall_point[0] > 0:
                    right_wall = self.get_tile(wall_point[0] - 1, math.floor(wall_point[1])).wall_right
                    if right_wall is not None:
                        highest_cover = max(highest_cover, right_wall.cover)
            else:
                # This wall is between two tiles vertically adjacent
                top_wall = self.get_tile(math.floor(wall_point[0]), wall_point[1]).wall_top
                if top_wall is not None:
                    highest_cover = max(highest_cover, top_wall.cover)
                if wall_point[1] > 0:
                    bottom_wall = self.get_tile(math.floor(wall_point[0]), wall_point[1] - 1).wall_bottom
                    if bottom_wall is not None:
                        highest_cover = max(highest_cover, bottom_wall.cover)

        return highest_cover

    def calculate_navgraph(self):
        self._navgraph = NavGraph()
        tile_pairs = set()

        for y in range(self._width):
            for x in range(self._height):
                # For each cell, look at the 3x3 square centered on it
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # Skip the cell itself
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        # Check if the neighboring cell is within the map
                        if 0 <= nx < self._width and 0 <= ny < self._height:
                            # sort the pair before adding to the set, to avoid duplicates
                            tile_pairs.add(tuple(sorted([(x, y), (nx, ny)])))

        for pair in tile_pairs:
            self._navgraph.add_node(pair[0])
            self._navgraph.add_node(pair[1])
            
            tile_1 = self.get_tile(pair[0][0], pair[0][1])
            tile_2 = self.get_tile(pair[1][0], pair[1][1])

            tile_1_costs = tile_1.movement_cost_onto(tile_2)
            tile_2_costs = tile_2.movement_cost_onto(tile_1)

            if tile_1_costs is not None:
                self._navgraph.add_edge(pair[0], pair[1], tile_1_costs)
            if tile_2_costs is not None:
                self._navgraph.add_edge(pair[1], pair[0], tile_2_costs)

        return self._navgraph

    def text_visualization(self):

        map_string = ""
        for y in range(self.height):
            row_string_middle = " " + (" " * (1 - int(y / 10))) + str(y) + " " 
            row_string_top = " " * len(row_string_middle)
            row_string_bottom = " " * len(row_string_middle)
            for x in range(self.width):
                tile_strings = self.get_tile(x, y).text_visualization()
                row_string_top += tile_strings[0]
                row_string_middle += tile_strings[1]
                row_string_bottom += tile_strings[2]
            map_string += row_string_top + "\n" + row_string_middle + "\n" + row_string_bottom + "\n"
        map_string += "  " + (" " * len(str(self.height - 1)))
        for x in range(self.width):
            map_string += "  " + str(x) + (" " * (1 - int(x / 10))) + " "
        return map_string.encode("utf-16").decode("utf-16")

    @staticmethod
    def load_from_file(path: str):
        with open(path, "r") as map_file:
            map_data = json.load(map_file)
            
            if map_data["details"]["version"] < Map.MAP_VERSION:
                return None
            
            width = int(map_data["details"]["width"])
            height = int(map_data["details"]["height"])

            map_grid = Map(width, height)

            for x in range(width):
                for y in range(height):
                    map_grid.set_tile(x, y, MapTile.from_data(map_data["map"][y][x]))

            return map_grid
        return None

    @staticmethod
    def dev_create(map_array: List[List[int]]):
        battlemap = Map(len(map_array[0]), len(map_array))
        for x in map_array:
            for y in map_array[x]:
                pass
        return battlemap

class MovementCost():
    def __init__(self, walking, flying = None, swimming = None, climbing = None, burrowing = None):
        self._walking = walking
        self._flying = walking if flying is None else flying
        self._swimming = swimming
        self._climbing = climbing
        self._burrowing = burrowing
    
    @property
    def walking(self):
        return self._walking
    
    @property
    def flying(self):
        return self._flying
    
    @property
    def swimming(self):
        return self._swimming
    
    @property
    def climbing(self):
        return self._climbing
    
    @property
    def burrowing(self):
        return self._burrowing
    
    @property
    def highest_speed(self):
        return max(filter(lambda v: v is not None, (self.walking, self.flying, self.swimming, self.climbing, self.burrowing)))

    @staticmethod
    def from_minimum_costs(first, second):
        if isinstance(first, MovementCost) and isinstance(second, MovementCost):
            return MovementCost(
                min(first.walking, second.walking),
                min(filter(lambda v: v is not None, (first.flying, second.flying)), default=None),
                min(filter(lambda v: v is not None, (first.swimming, second.swimming)), default=None),
                min(filter(lambda v: v is not None, (first.climbing, second.climbing)), default=None),
                min(filter(lambda v: v is not None, (first.burrowing, second.burrowing)), default=None)
            )
        else:
            raise TypeError("Unsupported operand type: can only add two MovementCost objects")
        
    def __add__(self, other):
        if isinstance(other, MovementCost):
            return MovementCost(
                self._walking + other.walking,
                sum(filter(lambda v: v is not None, (self.flying, other.flying))) if not (self._flying is None and other.flying is None) else None,
                sum(filter(lambda v: v is not None, (self.swimming, other.swimming))) if not (self._swimming is None and other.swimming is None) else None,
                sum(filter(lambda v: v is not None, (self.climbing, other.climbing))) if not (self._climbing is None and other.climbing is None) else None,
                sum(filter(lambda v: v is not None, (self.burrowing, other.burrowing))) if not (self._burrowing is None and other.burrowing is None) else None
            )
    
    def __radd__(self, other):
        if isinstance(other, MovementCost):
            return self.__add__(other)
        else:
            raise TypeError("Unsupported operand type: can only add two MovementCost objects")
    
    def __lt__(self, other):
        return self.highest_speed < other.highest_speed

class MapTile:
    def __init__(self, position = (-1, -1), passable = True, solid = False, movement_cost = MovementCost(5, 5), prop = None, wall_top = None, wall_bottom = None, wall_left = None, wall_right = None):
        self._position = position
        self._movement_cost = movement_cost
        self._passable = passable
        self._solid = solid
        self._prop = prop

        self._wall_top = wall_top
        self._wall_bottom = wall_bottom
        self._wall_left = wall_left
        self._wall_right = wall_right

    @staticmethod
    def from_data(load_data):
        return MapTile((load_data["x"], load_data["y"]), load_data["passable"], load_data["solid"], MovementCost(load_data["movement_cost"], load_data["movement_cost"]), load_data["prop"], WallFactory.from_data(load_data["walls"]["top"]), WallFactory.from_data(load_data["walls"]["bottom"]), WallFactory.from_data(load_data["walls"]["left"]), WallFactory.from_data(load_data["walls"]["right"]))

    @property
    def position(self):
        return self._position
    
    @property
    def x(self):
        return self._position[0]
    
    @property
    def y(self):
        return self._position[1]

    @property
    def passable(self):
        return self._passable and (self._prop is None or self._prop.passable)

    @property
    def solid(self):
        return self._solid

    @property
    def movement_cost(self):
        return self._movement_cost + (MovementCost(0) if (self._prop is None) else self._prop.movement_penalty)

    @property
    def cover(self):
        return 0 if self._prop is None else self._prop.cover

    @property
    def prop(self):
        return self._prop

    @prop.setter
    def prop(self, new_value):
        self._prop = new_value

    @property
    def wall_top(self):
        return self._wall_top

    @property
    def wall_bottom(self):
        return self._wall_bottom

    @property
    def wall_left(self):
        return self._wall_left

    @property
    def wall_right(self):
        return self._wall_right

    def movement_cost_onto(self, other):
        # Only takes into account the wall data on this tile and the inherent tile movement cost of the other tile.
        # Returns None if either the wall or the other tile are solid and therefore impassable.
        # Diagonals return value only if vertical and horizonal movement are possible.
        if other.solid:
            return None
        
        horizontal_wall = None
        vertical_wall = None

        offset_directions = 2

        if self.x < other.x:
            horizontal_wall = self._wall_left
        elif self.x > other.x:
            horizontal_wall = self._wall_right
        else:
            offset_directions -= 1

        if self.y < other.y:
            horizontal_wall = self._wall_top
        elif self.y > other.y:
            vertical_wall = self._wall_bottom
        else:
            offset_directions -= 1
            
        if offset_directions == 0:
            # Case to return None movement cost for moving onto tile at same coordinates
            return None
        elif offset_directions == 1:
            if self.y == other.y:
                if horizontal_wall is None:
                    return other.movement_cost
                elif not horizontal_wall.passable:
                    return None
            else:
                if vertical_wall is None:
                    return other.movement_cost
                elif not vertical_wall.passable:
                    return None
            return other.movement_cost + (horizontal_wall.movement_penalty if self.y == other.y else vertical_wall.movement_penalty)
        else:
            if horizontal_wall and not horizontal_wall.passable:
                return None
            elif vertical_wall and not vertical_wall.passable:
                return None
            return other.movement_cost + MovementCost.from_minimum_costs(MovementCost(0) if horizontal_wall is None else horizontal_wall.movement_penalty,
                                                                            MovementCost(0) if vertical_wall is None else vertical_wall.movement_penalty)
            

    def text_visualization(self):
        CORNER_PIECES = ["─┘", "└─", "─┐", "┌─", "═╛", "╘═", "═╕", "╒═", "─╜", "╙─", "─╖", "╓─", "═╝", "╚═", "═╗", "╔═"]
        EDGE_PIECES = ["─", "═", "│","║", "D", "D", "D", "D"]

        TILE_REPRESENTATION = "   "
        if self.movement_cost.walking > 5:
            TILE_REPRESENTATION = " * "
        elif self.solid:
            TILE_REPRESENTATION = "###"
        elif not self.passable:
            TILE_REPRESENTATION = "pit"

        def zero_or(value, condition):
            return value if condition else 0

        h_pipe_pos = 1
        v_pipe_pos = 2
        h_pipe_wall = 4
        v_pipe_wall = 8

        edge_wall = 1
        edge_vert = 2
        edge_door = 4

        return (
            CORNER_PIECES[h_pipe_pos + v_pipe_pos + zero_or(h_pipe_wall, self.wall_top is not None) + zero_or(v_pipe_wall, self.wall_left)] + EDGE_PIECES[zero_or(edge_door, isinstance(self.wall_top, TileDoor)) + zero_or(edge_wall, self.wall_top is not None)] + CORNER_PIECES[v_pipe_pos + zero_or(h_pipe_wall, self.wall_top is not None) + zero_or(v_pipe_wall, self.wall_right)],
            EDGE_PIECES[zero_or(edge_door, isinstance(self.wall_left, TileDoor)) + edge_vert + zero_or(edge_wall, self.wall_left is not None)] + TILE_REPRESENTATION + EDGE_PIECES[zero_or(edge_door, isinstance(self.wall_right, TileDoor)) + edge_vert + zero_or(edge_wall, self.wall_right is not None)],
            CORNER_PIECES[h_pipe_pos + zero_or(h_pipe_wall, self.wall_bottom is not None) + zero_or(v_pipe_wall, self.wall_left)] + EDGE_PIECES[zero_or(edge_door, isinstance(self.wall_bottom, TileDoor)) + zero_or(edge_wall, self.wall_bottom is not None)] + CORNER_PIECES[zero_or(h_pipe_wall, self.wall_bottom is not None) + zero_or(v_pipe_wall, self.wall_right)]
            )

class Interactable(ABC):
    _use_action = False
    _use_bonus_action = False
    _use_reaction = False
    _use_movement = False
    _use_object_interaction = False

    @abstractmethod
    def interact(self):
        pass

    @property
    def interactable(self):
        return self._use_action or self._use_bonus_action or self._use_reaction or self._use_movement

    @property
    def use_action(self):
        return self._use_action

    @property
    def use_bonus_action(self):
        return self._use_bonus_action

    @property
    def use_reaction(self):
        return self._use_reaction
    
    @property
    def use_movement(self):
        return self._use_movement

    @property
    def use_movement(self):
        return self._use_object_interaction

class WallFactory:
    @staticmethod
    def from_data(wall_data):
        if wall_data is None:
            return None
        if wall_data["type"] == "wall":
            return TileWall.from_data(wall_data)
        elif wall_data["type"] == "door":
            return TileDoor.from_data(wall_data)

class TileWall(Interactable):
    def __init__(self, cover = 3, passable = False, movement_penalty = MovementCost(0)):
        # cover value the wall provides: no cover = 0, half cover = 1, three-quarters cover = 2, full cover = 3
        self._cover = cover
        # whether or not the wall can be traversed
        self._passable = passable
        # movement penalty in feet the wall incurs for crossing over it
        self._movement_penalty = movement_penalty

    @staticmethod
    def from_data(load_data):
        return TileWall(load_data["cover"], load_data["passable"], MovementCost(load_data["movement_penalty"]))

    @property
    def passable(self):
        return self._passable
    
    @property
    def cover(self):
        return self._cover
    
    @property
    def movement_penalty(self):
        return self._movement_penalty

    def interact(self):
        pass

class TileDoor(TileWall):
    _use_object_interaction = True

    def __init__(self, cover = 3, passable = False, movement_penalty = MovementCost(0), locked = False, lockpick_dc = 0, hidden = False, discover_dc = 0):
        super().__init__(cover, passable, movement_penalty)
        self._closed_cover_value = cover
        self.locked = locked
        self._lockpick_dc = lockpick_dc
        self.hidden = hidden
        self._discover_dc = discover_dc

    @staticmethod
    def from_data(load_data):
        return TileDoor(load_data["cover"], load_data["passable"], MovementCost(load_data["movement_penalty"]), load_data["locked"], load_data["lockpick_dc"], load_data["hidden"], load_data["discover_dc"])

    @property
    def pick_dc(self):
        return self._lockpick_dc

    @property
    def discover_dc(self):
        return self._discover_dc

    def interact(self):
        self._cover = self._closed_cover_value - self._cover
        self._passable = not self._passable



class MapProp(Interactable):
    def __init__(self, cover, movement_penalty, passable, use_action = False, use_bonus_action = False, use_reaction = False, use_movement = False, use_object_interaction = False, interaction = None):
        super().__init__()
        self._cover = cover
        self._movement_penalty = movement_penalty
        self._passable = passable
        self._use_action = use_action
        self._use_bonus_action = use_bonus_action
        self._use_reaction = use_reaction
        self._use_movement = use_movement
        self._use_object_interaction = use_object_interaction
        self._interaction = interaction

    @property
    def cover(self):
        return self._cover

    @property
    def movement_penalty(self):
        return self._movement_penalty

    @property
    def passable(self):
        return self._passable

    def interact(self):
        if self._interaction is not None:
            return self._interaction()