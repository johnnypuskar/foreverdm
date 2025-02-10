import math
import json
from abc import ABC, abstractmethod
from typing import List, Tuple
from src.combat.map.navigation import NavGraph
from src.combat.map.movement import MovementCost
from src.combat.map.interactable import Interactable
from src.util.constants import Size
from src.util.grid_print import GridLine

import google.ai.generativelanguage as glm

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
        
        self._interactables = []
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @property
    def navgraph(self):
        return self._navgraph

    @property
    def interactables(self):
        return self._interactables

    def register_interactable(self, interactable):
        if not isinstance(interactable, Interactable):
            raise ValueError("Can only register Interactable objects.")
        if interactable not in self._interactables:
            self._interactables.append(interactable)
    
    def unregister_interactable(self, interactable):
        if interactable in self._interactables:
            self._interactables.remove(interactable)

    def get_tile(self, x, y):
        return self._grid[int(y)][int(x)]
    
    def set_tile(self, x: int, y: int, tile):
        self._grid[int(y)][int(x)] = tile

    def within_boundaries(self, x, y):
        return (0 <= x < self._width) and (0 <= y < self._height)

    def reregister_interactables(self):
        self._interactables.clear()
        for y in range(self._height):
            for x in range(self._width):
                tile = self.get_tile(x, y)
                if isinstance(tile.prop, Interactable):
                    self.register_interactable(tile.prop)
                if isinstance(tile.wall_top, Interactable):
                    self.register_interactable(tile.wall_top)
                if isinstance(tile.wall_bottom, Interactable):
                    self.register_interactable(tile.wall_bottom)
                if isinstance(tile.wall_left, Interactable):
                    self.register_interactable(tile.wall_left)
                if isinstance(tile.wall_right, Interactable):
                    self.register_interactable(tile.wall_right)

    def calculate_tiles_max_size(self):
        for x in range(self._width):
            for y in range(self._height):
                self.get_tile(x, y).max_token_size = self.calculate_max_size_at(x, y)

    def calculate_max_size_at(self, x, y):
        tile = self.get_tile(x, y)
        max_size = Size.MEDIUM
        tile_range = 1
        while max_size != Size.GARGANTUAN:
            for dx in range(tile_range):
                for dy in range(tile_range):
                    # Ignore previously checked tiles
                    if dx < tile_range - 1 and dy < tile_range - 1:
                        continue

                    # If any of the tiles are out of bounds, then the max size is the previous size
                    if not self.within_boundaries(x + dx, y + dy) or not self.within_boundaries(x + dx + 1, y + dy + 1):
                        return max_size
                    
                    horizontal_tile = self.get_tile(x + dx + 1, y + dy)
                    vertical_tile = self.get_tile(x + dx, y + dy + 1)
                    diagonal_tile = self.get_tile(x + dx + 1, y + dy + 1)

                    # If any of the tiles are solid, then the max size is the previous size
                    if any([tile.solid for tile in [tile, horizontal_tile, vertical_tile, diagonal_tile]]):
                        return max_size

                    # If any of the tiles have walls intersecting the center, then the max size is the previous size
                    if any([wall is not None for wall in [tile.wall_toward(1, 0), 
                                                          tile.wall_toward(0, 1), 
                                                          horizontal_tile.wall_toward(-1, 0),
                                                          horizontal_tile.wall_toward(0, 1),
                                                          vertical_tile.wall_toward(1, 0),
                                                          vertical_tile.wall_toward(0, -1),
                                                          diagonal_tile.wall_toward(-1, 0),
                                                          diagonal_tile.wall_toward(0, -1)]]):
                        return max_size
                    
                    # If any of the tiles have walking movement costs that are None (cannot be stood on), then the max size is the previous size
                    if any([tile.movement_cost.walking is None for tile in [tile, horizontal_tile, vertical_tile, diagonal_tile]]):
                        return max_size
            max_size = Size.next_size(max_size)
            tile_range += 1
        return max_size

    def get_tiles_in_line(self, start, end):
        # Based off Bresenham's line algorithm
        # https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
        if start == end:
            return [start]
        points = []
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:
            sign = int(abs(y2 - y1) / (y2 - y1))
            points = [(x1, y) for y in range(y1, min(y2, self._height), sign)]
            if y2 < self._height:
                points.append((x2, y2))
        elif y1 == y2:
            sign = int(abs(x2 - x1) / (x2 - x1))
            points = [(x, y1) for x in range(x1, min(x2, self._width), sign)]
            if x2 < self._width:
                points.append((x2, y2))
        elif abs(y2 - y1) < abs(x2 - x1):
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            dx = x2 - x1
            dy = y2 - y1
            yi = 1
            if dy < 0:
                yi = -1
                dy = -dy
            D = (2 * dy) - dx
            y = y1

            for x in range(x1, x2):
                points.append((x, y))
                if D > 0:
                    y += yi
                    D += 2 * (dy - dx)
                else:
                    D += 2 * dy
            points.append((x2, y2))
        else:
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1
            dx = x2 - x1
            dy = y2 - y1
            xi = 1
            if dx < 0:
                xi = -1
                dx = -dx
            D = (2 * dx) - dy
            x = x1

            for y in range(y1, y2):
                points.append((x, y))
                if D > 0:
                    x += xi
                    D += 2 * (dx - dy)
                else:
                    D += 2 * dx
            points.append((x2, y2))

        def distance_to_end(point):
            dx = end[0] - point[0]
            dy = end[1] - point[1]
            return math.sqrt(dx*dx + dy*dy)
            
        points = [point for point in points if 0 <= point[0] < self._width and 0 <= point[1] < self._height]
        points.sort(key=distance_to_end, reverse=True)
        return points


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

    def calculate_movement_cost(self, from_pos, to_pos, size = 0):
        # Returns the cost of moving from one tile to another
        # Size is factored in, assuming positions are at the top left of the token and tiles are 5x5ft
        # Will return None if the tiles are not adjacent, or if the move is to the same tile
        # Will return None if the move is not possible due to obstruction

        # Returns none if locations are outside of map boundaries
        if not self.within_boundaries(from_pos[0], from_pos[1]) or not self.within_boundaries(to_pos[0], to_pos[1]):
            return None

        # Returns none if movement locations are invalid
        if abs(from_pos[0] - to_pos[0]) > 1 or abs(from_pos[1] - to_pos[1]) > 1 or from_pos == to_pos:
            return None
        
        # Returns none if tile cannot accomodate token size
        if self.get_tile(to_pos[0], to_pos[1]).max_token_size < size:
            return None

        # Gets destination Tile and returns none if Tile is solid
        to_tile = self.get_tile(to_pos[0], to_pos[1])
        if to_tile.solid:
            return None

        from_tile = self.get_tile(from_pos[0], from_pos[1])
        movement_direction = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])

        movement_cost = None
        if movement_direction[0] == 0 or movement_direction[1] == 0:
            # Adjacent movement
            wall = from_tile.wall_toward(movement_direction[0], movement_direction[1])
            if wall is None:
                movement_cost = to_tile.movement_cost
            elif not wall.passable:
                return None
            else:
                movement_cost = to_tile.movement_cost + wall.movement_penalty
        else:
            # Diagonal movement
            hx, hy = from_pos[0] + movement_direction[0], from_pos[1]
            vx, vy = from_pos[0], from_pos[1] + movement_direction[1]

            horizontal_tile = self.get_tile(hx, hy)
            vertical_tile = self.get_tile(vx, vy)

            # Create lists of walls that must be considered for movement
            horizontal_walls = [wall for wall in [from_tile.wall_toward(movement_direction[0], 0), horizontal_tile.wall_toward(0, movement_direction[1])] if wall is not None]
            vertical_walls = [wall for wall in [from_tile.wall_toward(0, movement_direction[1]), vertical_tile.wall_toward(movement_direction[0], 0)] if wall is not None]

            # Returns none if any walls are impassable        
            if any(not wall.passable for wall in horizontal_walls + vertical_walls):
                return None
            
            movement_cost = to_tile.movement_cost + min(sum([MovementCost(0)] + [wall.movement_cost for wall in horizontal_walls]), sum([MovementCost(0)] + [wall.movement_cost for wall in vertical_walls]))
        
        # Handle sizes larger than Medium
        if size > Size.MEDIUM:
            alt_movement_cost = None
            for cols in range(1, int(size / Size.GRID_SIZE)):
                alt_movement_cost = self.calculate_movement_cost((from_pos[0] + cols, from_pos[1]), (to_pos[0] + cols, to_pos[1]))
                if alt_movement_cost is None:
                    return None
                movement_cost = max(movement_cost, alt_movement_cost)

            for rows in range(1, int(size / Size.GRID_SIZE)):
                alt_movement_cost = self.calculate_movement_cost((from_pos[0], from_pos[1] + rows), (to_pos[0], to_pos[1] + rows))
                if alt_movement_cost is None:
                    return None
                movement_cost = max(movement_cost, alt_movement_cost)
            
            alt_movement_cost = self.calculate_movement_cost((from_pos[0] + 1, from_pos[1] + 1), (to_pos[0] + 1, to_pos[1] + 1), size - Size.GRID_SIZE)
            if alt_movement_cost is None:
                return None
            
            movement_cost = max(movement_cost, alt_movement_cost)
        return movement_cost
            
    def calculate_navgraph(self):
        self.calculate_tiles_max_size()
        self._navgraph = NavGraph()

        # Create a set of all pairs of adjacent and diagonal tiles
        tile_pairs = set()
        for x in range(self._width):
            for y in range(self._height):
                # For each cell, look at the 3x3 square centered on it
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        # Skip the cell itself
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        # Check if the neighboring cell is within the map
                        if 0 <= nx < self._width and 0 <= ny < self._height:
                            # Sort the pair before adding to the set, to avoid duplicates
                            tile_pairs.add(tuple(sorted([(x, y), (nx, ny)])))

        # Add tiles as nodes to the navgraph
        for pair in tile_pairs:
            if pair[0] not in self._navgraph.nodes:
                self._navgraph.add_node(pair[0], self.get_tile(pair[0][0], pair[0][1]).max_token_size)
            if pair[1] not in self._navgraph.nodes:
                self._navgraph.add_node(pair[1], self.get_tile(pair[1][0], pair[1][1]).max_token_size)

            # Add node neighbors
            if self.calculate_movement_cost(pair[0], pair[1]) is not None:
                self._navgraph.nodes[pair[0]].add_neighbor(pair[1])
            if self.calculate_movement_cost(pair[1], pair[0]) is not None:
                self._navgraph.nodes[pair[1]].add_neighbor(pair[0])
        
        return self._navgraph

    def add_prop(self, prop, position: Tuple[int, int]):
        if not isinstance(prop, MapProp):
            raise ValueError("Can only add MapProp objects to map.")
        if not self.within_boundaries(position[0], position[1]):
            raise ValueError("Position must be within map boundaries.")
        self.get_tile(position[0], position[1]).prop = prop
        self.register_interactable(prop)

    def remove_prop(self, prop):
        if prop in self._interactables:
            self.get_tile(prop.position[0], prop.position[1]).prop = None
            self.unregister_interactable(prop)

    def remove_prop_at(self, position: Tuple[int, int]):
        if not self.within_boundaries(position[0], position[1]):
            raise ValueError("Position must be within map boundaries.")
        if self.get_tile(position[0], position[1]).prop is not None:
            self.unregister_interactable(self.get_tile(position[0], position[1]).prop)
        self.get_tile(position[0], position[1]).prop = None

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
            
            map_grid.calculate_navgraph()
            map_grid.reregister_interactables()

            return map_grid

    def get_map_as_string(self, highlighted = []):
        string_width = 6 * (self._width + 1) + 4
        
        col_label_string = " " * 7
        for x in range(self._width):
            col_label_string += f"  {x:^4}"
        
        def insert_into_map_string(m_string, x, y, row_1, row_2, row_3):
            tile_text_index = (y * string_width * 2) + 6 * x

            m_string = m_string[:tile_text_index] + row_1 + map_string[tile_text_index + len(row_1):]
            m_string = m_string[:tile_text_index + string_width] + row_2 + map_string[tile_text_index + string_width + len(row_2):]
            m_string = m_string[:tile_text_index + 2 * string_width] + row_3 + map_string[tile_text_index + 2 * string_width + len(row_3):]

            return m_string


        map_string = ("[/]" * (3 * self._width - 1) + "\n") * (1 + 2 * self._height)

        TILE_CHAR_WIDTH = 9

        for y in range(self._height):
            map_string = insert_into_map_string(map_string, 0, y, " " * 6, f" {y:>4} ", " " * 6)
            for x in range(self._width):

                # Top Row
                wall_up = False
                wall_down = False
                wall_left = False
                wall_right = False 

                try:
                    if y > 0:
                        wall_up = self.get_tile(x, y - 1).wall_left is not None or self.get_tile(x - 1, y - 1).wall_right is not None
                except IndexError:
                    pass

                try:
                    wall_down = self.get_tile(x, y).wall_left is not None or self.get_tile(x - 1, y).wall_right is not None
                except IndexError:
                    pass

                try:
                    wall_right = self.get_tile(x, y).wall_top is not None or self.get_tile(x, y - 1).wall_bottom is not None
                except IndexError:
                    pass

                try:
                    if x > 0:
                        wall_left = self.get_tile(x - 1, y).wall_top is not None or self.get_tile(x - 1, y - 1).wall_bottom is not None
                except IndexError:
                    pass

                top_row = str(GridLine.without_wall(GridLine.CORNER))
                if any([wall_up, wall_down, wall_left, wall_right]):
                    top_row = str(GridLine.with_wall(wall_up, wall_down, wall_left, wall_right))

                if wall_right:
                    top_row += str(GridLine.with_wall(False, False, True, True))
                else:
                    top_row += str(GridLine.without_wall(GridLine.HORIZONTAL))
                
                wall_side_up = False
                wall_side_down = self.get_tile(x, y).wall_right is not None

                try:
                    if y > 0:
                        wall_side_up = self.get_tile(x, y - 1).wall_right is not None
                except IndexError:
                    pass

                if any([wall_side_up, wall_side_down, wall_right]):
                    top_row += str(GridLine.with_wall(wall_side_up, wall_side_down, wall_right, False))
                else:
                    top_row += str(GridLine.without_wall(GridLine.CORNER))

                # Middle Row
                wall_middle_right = False
                try:
                    wall_middle_right = self.get_tile(x, y).wall_right is not None or self.get_tile(x + 1, y).wall_left is not None
                except IndexError:
                    pass

                middle_row = str(GridLine.without_wall(GridLine.VERTICAL))
                if wall_down:
                    middle_row = str(GridLine.with_wall(True, True, False, False))
                
                if (x, y) in highlighted:
                    middle_row += "(@)"
                else:
                    middle_row += self.get_tile(x, y).center_string

                if wall_middle_right:
                    middle_row += str(GridLine.with_wall(True, True, False, False))
                else:
                    middle_row += str(GridLine.without_wall(GridLine.VERTICAL))

                # Bottom Row
                wall_bottom_left = False
                wall_bottom_right = self.get_tile(x, y).wall_bottom is not None

                try:
                    if x > 0:
                        wall_bottom_left = self.get_tile(x - 1, y).wall_bottom is not None
                except IndexError:
                    pass
                
                bottom_row = str(GridLine.without_wall(GridLine.CORNER))
                if any([wall_bottom_left, wall_down, wall_bottom_right]):
                    bottom_row = str(GridLine.with_wall(wall_down, False, wall_bottom_left, wall_bottom_right))
                
                if wall_bottom_right:
                    bottom_row += str(GridLine.with_wall(False, False, True, True))
                else:
                    bottom_row += str(GridLine.without_wall(GridLine.HORIZONTAL))
                
                if any([wall_bottom_right, wall_side_down]):
                    bottom_row += str(GridLine.with_wall(wall_side_down, False, wall_bottom_right, False))
                else:
                    bottom_row += str(GridLine.without_wall(GridLine.CORNER))
                
                if x == self._width - 1:
                    top_row += "\n"
                    middle_row += "\n"
                    bottom_row += "\n"

                map_string = insert_into_map_string(map_string, x + 1, y, top_row, middle_row, bottom_row)

        return "\n" + col_label_string + "\n" + map_string[:string_width * (self._height * 2 + 1) - 1]

    def __str__(self):
        return self.get_map_as_string()

class MapTile:
    def __init__(self, position = (-1, -1), movement_cost = MovementCost(5), prop = None, wall_top = None, wall_bottom = None, wall_left = None, wall_right = None):
        self._position = position
        self._movement_cost = movement_cost
        self._solid = movement_cost.has_no_movement
        self._prop = prop

        self.max_token_size = Size.MEDIUM

        self._wall_top = wall_top
        if isinstance(self._wall_top, Interactable):
            self._wall_top.position = self._position
        self._wall_bottom = wall_bottom
        if isinstance(self._wall_bottom, Interactable):
            self._wall_bottom.position = self._position
        self._wall_left = wall_left
        if isinstance(self._wall_left, Interactable):
            self._wall_left.position = self._position
        self._wall_right = wall_right
        if isinstance(self._wall_right, Interactable):
            self._wall_right.position = self._position

    @staticmethod
    def from_data(load_data):
        return MapTile((load_data["x"], load_data["y"]),MovementCost(load_data["movement_cost"]["walking"], load_data["movement_cost"]["flying"], load_data["movement_cost"]["swimming"], load_data["movement_cost"]["climbing"], load_data["movement_cost"]["burrowing"]), load_data["prop"], WallFactory.from_data(load_data["walls"]["top"]), WallFactory.from_data(load_data["walls"]["bottom"]), WallFactory.from_data(load_data["walls"]["left"]), WallFactory.from_data(load_data["walls"]["right"]))

    @property
    def position(self):
        return self._position
    
    @property
    def x(self):
        return self._position[0]
    
    @property
    def y(self):
        return self._position[1]
        return self._passable and (self._prop is None or self._prop.passable)

    @property
    def solid(self):
        return self._solid

    @property
    def movement_cost(self):
        return self._movement_cost + (MovementCost(0, 0, 0, 0, 0) if (self._prop is None) else self._prop.movement_penalty)

    @property
    def cover(self):
        return 0 if self._prop is None else self._prop.cover

    @property
    def prop(self):
        return self._prop

    @prop.setter
    def prop(self, new_value):
        if isinstance(new_value, MapProp):
            if self._prop is not None:
                self._prop.position = None
            self._prop = new_value
            self._prop.position = self._position

    def wall_toward(self, x_dir, y_dir):
        if x_dir != 0 and y_dir != 0:
            raise ValueError("Cannot return single wall in diagonal direction.")
        if x_dir == 0:
            if y_dir == 1:
                return self._wall_bottom
            elif y_dir == -1:
                return self._wall_top
        else:
            if x_dir == 1:
                return self._wall_right
            elif x_dir == -1:
                return self._wall_left

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

    @property
    def center_string(self):
        TILE_REPRESENTATION = "   "
        if self.solid:
            TILE_REPRESENTATION = "###"
        elif self._movement_cost.walking is None:
            TILE_REPRESENTATION = "pit"
        elif self._movement_cost.walking > 5:
            if self._movement_cost.swimming is not None and self._movement_cost.swimming > 0:
                TILE_REPRESENTATION = "~~~"
            else:
                TILE_REPRESENTATION = " * "
        
        return TILE_REPRESENTATION

# class Interactable(ABC):
#     _use_action = False
#     _use_bonus_action = False
#     _use_reaction = False
#     _use_movement = False
#     _use_object_interaction = False

#     @abstractmethod
#     def interact(self):
#         pass

#     @property
#     def interactable(self):
#         return self._use_action or self._use_bonus_action or self._use_reaction or self._use_movement

#     @property
#     def use_action(self):
#         return self._use_action

#     @property
#     def use_bonus_action(self):
#         return self._use_bonus_action

#     @property
#     def use_reaction(self):
#         return self._use_reaction
    
#     @property
#     def use_movement(self):
#         return self._use_movement

#     @property
#     def use_movement(self):
#         return self._use_object_interaction

class WallFactory:
    @staticmethod
    def from_data(wall_data):
        if wall_data is None:
            return None
        if wall_data["type"] == "wall":
            return TileWall.from_data(wall_data)
        elif wall_data["type"] == "door":
            return TileDoor.from_data(wall_data)

class TileWall:
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


class TileDoor(TileWall, Interactable):
    _use_object_interaction = True

    def __init__(self, name = "Door", description = "An unlocked door. Closed.", cover = 3, passable = False, movement_penalty = MovementCost(0)):
        TileWall.__init__(self, cover, passable, movement_penalty)
        Interactable.__init__(self, name, description)
        self._closed_cover_value = cover

        self._position = None

    @staticmethod
    def from_data(load_data):
        return TileDoor(load_data["cover"], load_data["passable"], MovementCost(load_data["movement_penalty"]))

    def update_func_declaration(self):
        return glm.FunctionDeclaration(
            name = 'interact',
            description = 'Sets the description of this door as a result of an interaction, as well as its opened boolean value.',
            parameters = glm.Schema(
                type = glm.Type.OBJECT,
                properties = {
                    'new_description': glm.Schema(type = glm.Type.STRING),
                    'opened': glm.Schema(type = glm.Type.BOOLEAN)
                },
                required = ['new_description', 'opened']
            )
        )

    def update(self, new_description, opened):
        self._cover = 0 if opened else self._closed_cover_value
        self._passable = opened
        return super().update(new_description)

class MapProp(Interactable):
    def __init__(self, name, description, cover = 0, movement_penalty = MovementCost(0), passable = True):
        super().__init__(name, description)
        self._cover = cover
        self._movement_penalty = movement_penalty
        self._passable = passable

        self._position = None

    @property
    def cover(self):
        return self._cover

    @property
    def movement_penalty(self):
        return self._movement_penalty

    @property
    def passable(self):
        return self._passable

    def update_func_declaration(self):
        return glm.FunctionDeclaration(
            name = 'interact',
            description = 'Sets the description of this door as a result of an interaction, as well as its opened boolean value.',
            parameters = glm.Schema(
                type = glm.Type.OBJECT,
                properties = {
                    'new_description': glm.Schema(type = glm.Type.STRING),
                    'cover': glm.Schema(type = glm.Type.INTEGER, description = 'The cover value the prop provides, must be an integer 0-3 inclusive: 0 = no cover, 1 = half cover, 2 = three-quarters cover, 3 = full cover'),
                    'movement_penalty': glm.Schema(type = glm.Type.OBJECT, description = 'The additional movement cost this prop incurs when moving over it with various movement types. Each penalty value must be an integer 0 or greater.', properties = {
                        'walking': glm.Schema(type = glm.Type.INTEGER, description = 'Walking speed penalty.'),
                        'flying': glm.Schema(type = glm.Type.INTEGER, description = 'Flying speed penalty.'),
                        'swimming': glm.Schema(type = glm.Type.INTEGER, description = 'Swimming speed penalty.'),
                        'climbing': glm.Schema(type = glm.Type.INTEGER, description = 'Climbing speed penalty.'),
                        'burrowing': glm.Schema(type = glm.Type.INTEGER, description = 'Burrowing speed penalty.')
                    }),
                    'passable': glm.Schema(type = glm.Type.BOOLEAN, description = 'Whether or not this prop can be traversed over.')
                },
                required = ['new_description']
            )
        )

    def update(self, new_description, cover = None, movement_penalty = None, passable = None):
        self._cover = cover if cover is not None else self.cover
        self._movement_penalty = movement_penalty if movement_penalty is not None else self.movement_penalty
        self._passable = passable if passable is not None else self.passable
        return super().update(new_description)