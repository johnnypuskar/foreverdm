from __future__ import annotations
import math

class Room:
    
    def __init__(self, width, height):
        self._width = width
        self._height = height

        self.tiles = set()
        self.adjacent_tiles = {}
    
    def calculate_adjacent_tiles(self):
        self.adjacent_tiles = {}
        for (x, y) in self.tiles:
            for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                offset_tile = (x + dx, y + dy)
                if offset_tile not in self.tiles:
                    self.adjacent_tiles[offset_tile] = self.adjacent_tiles.get(offset_tile, 0) + 1
        return self.adjacent_tiles

    def is_out_of_bounds(self, x, y):
        return x < 0 or x >= self._width or y < 0 or y >= self._height

    def has_tile_at(self, x, y):
        if self.is_out_of_bounds(x, y):
            return False
        return (x, y) in self.tiles
    
    # Function to find the amount of tile adjacencies between two rooms, given that other room is offset
    # Returns multiple values:
    #   - bool: whether the rooms overlap
    #   - int: the number of adjacent tiles
    def find_adjacencies(self, other: Room, offset: tuple[int, int]):
        adjacencies = 0
        for tile in other.tiles:
            offset_tile = (tile[0] + offset[0], tile[1] + offset[1])
            if offset_tile in self.tiles:
                return (True, -1)
            if offset_tile in self.adjacent_tiles:
                adjacencies += self.adjacent_tiles[offset_tile]
        return (False, adjacencies)
