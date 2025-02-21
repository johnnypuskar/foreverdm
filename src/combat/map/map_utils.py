import math
from src.combat.map.map_tile_wall import MapTileWall

class MapUtils:
    def __init__(self, map):
        self._map = map
    
    def get_tiles_in_line(self, start, end):
        """
        Returns a list of connected tiles between two points.
        Function ignores height, and returned points will all be at the height of the start point.
        
        Based off Bresenham's line algorithm for 3D points.

        param start: tuple[int, int, int] - The starting point.
        param end: tuple[int, int, int] - The ending point.
        return: list[tuple[int, int, int]] - A list of points between the start and end points, ordered from start to end
        """
        points = [start]
        x1, y1, z1 = start
        x2, y2, z2 = end
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        dz = abs(z2 - z1)
        xs = 1 if x2 > x1 else -1
        ys = 1 if y2 > y1 else -1
        zs = 1 if z2 > z1 else -1

        if dx >= dy and dx >= dz:
            p1 = 2 * dy - dx
            p2 = 2 * dz - dx
            while (x1 != x2):
                x1 += xs
                if (p1 >= 0):
                    y1 += ys
                    p1 -= 2 * dx
                if (p2 >= 0):
                    z1 += zs
                    p2 -= 2 * dx
                p1 += 2 * dy
                p2 += 2 * dz
                points.append((x1, y1, z1))
        elif dy >= dx and dy >= dz:    
            p1 = 2 * dx - dy
            p2 = 2 * dz - dy
            while (y1 != y2):
                y1 += ys
                if (p1 >= 0):
                    x1 += xs
                    p1 -= 2 * dy
                if (p2 >= 0):
                    z1 += zs
                    p2 -= 2 * dy
                p1 += 2 * dx
                p2 += 2 * dz
                points.append((x1, y1, z1))
        else:
            p1 = 2 * dy - dz
            p2 = 2 * dx - dz
            while (z1 != z2):
                z1 += zs
                if (p1 >= 0):
                    y1 += ys
                    p1 -= 2 * dz
                if (p2 >= 0):
                    x1 += xs
                    p2 -= 2 * dz
                p1 += 2 * dy
                p2 += 2 * dx
                points.append((x1, y1, z1))
        return points
    
    def get_wall_points_in_line(self, start, end):
        tiles = self.get_tiles_in_line(start, end)
        if len(tiles) == 1:
            return []
        wall_points = []

        for i in range(len(tiles) - 1):
            tile_pos = tiles[i]
            next_tile_pos = tiles[i + 1]
            if tile_pos[0] != next_tile_pos[0]:
                wall_points.append((tile_pos[0], tile_pos[1], tile_pos[2], MapTileWall.WallDirection.RIGHT if tile_pos[0] < next_tile_pos[0] else MapTileWall.WallDirection.LEFT))
                # Only add opposite matching wall if next tile is also shifted in the y direction, and is not higher than the current tile (provides height advantage)
                # Exception for walls directly next to end tile, as it could feel strange to not get cover bonus from a directly adjacent wall
                if tile_pos[1] != next_tile_pos[1] and (tile_pos[2] <= next_tile_pos[2] or next_tile_pos == end):
                    wall_points.append((next_tile_pos[0], next_tile_pos[1], next_tile_pos[2], MapTileWall.WallDirection.LEFT if tile_pos[0] < next_tile_pos[0] else MapTileWall.WallDirection.RIGHT))
            if tile_pos[1] != next_tile_pos[1]:
                wall_points.append((tile_pos[0], tile_pos[1], tile_pos[2], MapTileWall.WallDirection.TOP if tile_pos[1] < next_tile_pos[1] else MapTileWall.WallDirection.BOTTOM))
                # Only add opposite matching wall if next tile is also shifted in the y direction, and is not higher than the current tile (provides height advantage)
                # Exception for walls directly next to end tile, as it could feel strange to not get cover bonus from a directly adjacent wall
                if tile_pos[0] != next_tile_pos[0] and (tile_pos[2] <= next_tile_pos[2] or next_tile_pos == end):
                    wall_points.append((next_tile_pos[0], next_tile_pos[1], next_tile_pos[2], MapTileWall.WallDirection.BOTTOM if tile_pos[1] < next_tile_pos[1] else MapTileWall.WallDirection.TOP))
        
        return wall_points