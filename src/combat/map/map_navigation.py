from __future__ import annotations
import heapq
from src.combat.map.map import Map

class NavigationHandler:
    # Tile size in feet.
    TILE_SIZE = 5

    TILE_DIAGONAL = int(TILE_SIZE * 1.414)
    TILE_VERT_DIAGONAL = int(TILE_SIZE * 1.732)

    def __init__(self, map: Map):
        self._map = map

        self._node_graph = {}

        for x in range(self._map.width):
            for y in range(self._map.height):
                for h in range(self._map._max_height):
                    self._node_graph[(x, y, h)] = NavNode((x, y, h))
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            for dh in range(-1, 2):
                                if dx == 0 and dy == 0 and dh == 0:
                                    continue
                                if not self._node_graph.get((x + dx, y + dy, h + dh)):
                                    continue
                                DISTANCES = [NavigationHandler.TILE_SIZE, NavigationHandler.TILE_DIAGONAL, NavigationHandler.TILE_VERT_DIAGONAL]
                                distance = DISTANCES[abs(dx) + abs(dy) + abs(dh) - 1]
                                self._node_graph[(x, y, h)].add_neighbor(self._node_graph[(x + dx, y + dy, h + dh)], distance)
    
    class Path:
        def __init__(self, path, distance):
            self.path = path
            self.distance = distance
        
        @property
        def start(self):
            return self.path[0]
        
        @property
        def end(self):
            return self.path[-1]

    def get_all_paths(self, statblock, start):
        """
        Returns a dictionary of all paths to other nodes from the start node with the given statblock.

        param statblock: Statblock - the statblock of the entity
        param start: tuple - the starting position, format: (x, y, height)

        returns: dict[tuple, list[tuple]] - the dictionary of paths to other nodes
        """
        start_node = self._node_graph[start]
        distances = {node._position3D: float('inf') for node in self._node_graph.values()}
        previous = {node: None for node in self._node_graph.values()}
        distances[start_node._position3D] = 0

        queue = [(0, start_node)]
        paths = {start_node._position3D: NavigationHandler.Path([start_node._position3D], 0)}
        
        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_distance > distances[current_node._position3D]:
                continue

            for neighbor in current_node.neighbors:
                base_distance = distances[current_node._position3D]

                # Extracted finding traversal cost into function to allow for more direct and easier testing
                traversal_cost = self._get_traversal_distance(base_distance, statblock, current_node, neighbor)
                if traversal_cost is None:
                    continue

                distance = base_distance + traversal_cost
                if distance < distances[neighbor.node._position3D]:
                    distances[neighbor.node._position3D] = distance
                    previous[neighbor.node] = current_node
                    heapq.heappush(queue, (distance, neighbor.node))
                    paths[neighbor.node._position3D] = NavigationHandler.Path(paths[current_node._position3D].path + [neighbor.node._position3D], distance)

        return paths

    def _get_traversal_distance(self, base_distance, statblock, current, destination):
        """
        Returns the amount of feet of movement it takes to move from the current node to the destination node, given a base distance already moved as a statblock.

        param base_distance: int - the distance already moved
        param statblock: Statblock - the statblock of the entity
        param current: NavNode - the current node
        param destination: NavNode - the destination node

        returns:
            int - the distance of movement to the destination node
            None - if the destination is unreachable
        """
        speed = statblock.get_speed()
        tile = self._map.get_tile(*destination.node.position)
        ft_mult = 1 + tile.terrain_difficulty
        traversal_distance = 0

        if destination.node.height > tile.height:
            # Destination is above tile ground level, movement will use flight or climb/walk speed.
            neighbor_distance = destination.distance
            distance_fly = min(max(0, speed.fly - base_distance), neighbor_distance)
            neighbor_distance -= distance_fly
            traversal_distance += distance_fly
            
            if neighbor_distance <= 0:
                return traversal_distance

            # Only allow climbing if the current position is climbable and the destination is climbable or at floor height.
            cur_climb_dc = self._map.get_climb_dc(*current.position, current.height)
            des_climb_dc = self._map.get_climb_dc(*destination.node.position, destination.node.height)
            if cur_climb_dc is not None and (des_climb_dc is not None or destination.node.height == tile.height):
                distance_climb = min(max(0, speed.climb - base_distance), neighbor_distance)
                neighbor_distance -= distance_climb
                traversal_distance += distance_climb
                if neighbor_distance <= 0:
                    return traversal_distance
                
                distance_walk = min(max(0, speed.walk - base_distance), neighbor_distance)
                neighbor_distance -= distance_walk
                traversal_distance += distance_walk * (1 + ft_mult)
                if neighbor_distance <= 0:
                    return traversal_distance
        elif tile.swimmable:
            # Destination is at or below ground level, and swimmable, movement will use flight or swim/walk speed.
            if destination.node.height >= tile._max_depth:
                return None
            
            neighbor_distance = destination.distance

            if destination.node.height == tile.height:
                distance_fly = min(max(0, speed.fly - base_distance), neighbor_distance)
                neighbor_distance -= distance_fly
                traversal_distance += distance_fly
                if neighbor_distance <= 0:
                    return traversal_distance
                
            distance_swim = min(max(0, speed.swim - base_distance), neighbor_distance)
            neighbor_distance -= distance_swim
            traversal_distance += distance_swim * ft_mult
            if neighbor_distance <= 0:
                return traversal_distance
            
            distance_walk = min(max(0, speed.walk - base_distance), neighbor_distance)
            neighbor_distance -= distance_walk
            traversal_distance += distance_walk * (1 + ft_mult)
            if neighbor_distance <= 0:
                return traversal_distance
        elif destination.node.height < tile.height:
            # Destination is not swimmable, and below ground level, movement must use burrow speed.
            if destination.node.height >= tile._max_depth and max(0, speed.burrow - base_distance) >= destination.distance:
                return destination.distance
        else:
            # Movement is at ground level, movement will use flight or walk speed.
            neighbor_distance = destination.distance
            distance_fly = min(max(0, speed.fly - base_distance), neighbor_distance)
            neighbor_distance -= distance_fly
            traversal_distance += distance_fly
            if neighbor_distance <= 0:
                return traversal_distance
            
            distance_walk = min(max(0, speed.walk - base_distance), neighbor_distance)
            neighbor_distance -= distance_walk
            traversal_distance += distance_walk * ft_mult
            if neighbor_distance <= 0:
                return traversal_distance
        return None

    def get_path(self, statblock, start, end):
        """
        Returns a list of positions that represent the shortest path from start to end, given the statblock of the entity.
        If no path is possible with the given statblock, returns None.

        param speed: statblock - the statblock of the entity
        param start: tuple - the starting position, format: (x, y, height)
        param end: tuple - the ending position, format: (x, y, height)

        returns:
            list[Path] - if path exists, the list of positions from start to end
            None - if no path exists
        """
        return self._get_all_paths(statblock, start).get(end, None)


class NavNode:
    def __init__(self, position3D):
        self._position3D = position3D
        self.neighbors = set()

    class Neighbor:
        def __init__(self, neighbor, distance):
            self.node = neighbor
            self.distance = distance
        
        def __eq__(self, other):
            return self.node == other.node and self.distance == other.distance
        
        def __hash__(self):
            return hash((self.node, self.distance))
    
    @property
    def position(self):
        return self._position3D[:2]
    
    @property
    def height(self):
        return self._position3D[2]

    def add_neighbor(self, neighbor: NavNode, distance):
        self.neighbors.add(NavNode.Neighbor(neighbor, distance))
        neighbor.neighbors.add(NavNode.Neighbor(self, distance))
    
    def __hash__(self):
        return hash(self._position3D)
    
    def __lt__(self, other):
        return self._position3D < other._position3D

    def __repr__(self):
        return f"<NavNode {self._position3D} {len(self.neighbors)}*>"