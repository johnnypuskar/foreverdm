import math
from src.combat.map.map_tile_wall import MapTileWall

class MapUtils:
    def __init__(self, map):
        self._map = map
    
    def get_wall_points_in_line(self, start, end):
        if start == end:
            return []
        wall_points = []
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:
            for i in range(min(y1, y2), max(y1, y2) + 1):
                wall_points.append((x1, i + 0.5))
        elif y1 == y2:
            for i in range(min(x1, x2), max(x1, x2) + 1):
                wall_points.append((i + 0.5, y1))
        else:
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            for x in range(x1 + 1, x2):
                y = m * x + b
                wall_points.append((x, int(y) + 0.5))
            for y in range(y1 + 1, y2):
                x = (y - b) / m
                wall_points.append((int(x) + 0.5, y))
        
        def distance_to_end(point):
            dx = end[0] - point[0]
            dy = end[1] - point[1]
            return math.sqrt(dx*dx + dy*dy)
        
        wall_points.sort(key=distance_to_end, reverse=True)
        for i in range(len(wall_points)):
            wall_x, wall_y = wall_points[i]
            if math.isclose(wall_x, round(wall_x)):
                wall_points[i] = (int(wall_x - 1), int(wall_y), MapTileWall.WallDirection.RIGHT) if wall_x >= self._map._width else (int(wall_x), int(wall_y), MapTileWall.WallDirection.LEFT)
            else:
                wall_points[i] = (int(wall_x), int(wall_y - 1), MapTileWall.WallDirection.BOTTOM) if wall_y >= self._map._height else (int(wall_x), int(wall_y), MapTileWall.WallDirection.TOP)
        return [wall_point for wall_point in wall_points if 0 <= wall_point[0] < self._map._width and 0 <= wall_point[1] < self._map._height]

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
            points = [(x1, y) for y in range(y1, min(y2, self._map._height), sign)]
            if y2 < self._map._height:
                points.append((x2, y2))
        elif y1 == y2:
            sign = int(abs(x2 - x1) / (x2 - x1))
            points = [(x, y1) for x in range(x1, min(x2, self._map._width), sign)]
            if x2 < self._map._width:
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
            
        points = [point for point in points if 0 <= point[0] < self._map._width and 0 <= point[1] < self._map._height]
        points.sort(key=distance_to_end, reverse=True)
        return points