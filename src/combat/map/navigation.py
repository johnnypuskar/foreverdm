from src.combat.map.movement import MovementCost
import heapq

class NavNode:
    def __init__(self, position, max_size):
        self.position = position
        self.neighbors = set()
        self.previous = None
        self.max_size = max_size

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)
    
    def __lt__(self, other):
        return self.position < other.position

class NavGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, position, max_size):
        if position in self.nodes:
            return
        node = NavNode(position, max_size)
        self.nodes[position] = node
        return node

    def connect_neighbor(self, from_position, to_position):
        if from_position not in self.nodes or to_position not in self.nodes:
            raise ValueError("Both nodes must exist to connect as neighbors.")
        self.nodes[from_position].add_neighbor(self.nodes[to_position])

class NavAgent:
    def __init__(self, speed, size):
        self.speed = speed
        self.size = size

    def get_reachable_nodes(self, map, start_position, ignore_positions = []):
        start_node = map.navgraph.nodes[start_position]
        distances = {node: float('inf') for node in map.navgraph.nodes}
        previous = {node: None for node in map.navgraph.nodes}
        distances[start_node.position] = 0

        queue = [(0, start_node)]
        reachable_nodes = {start_position: self.speed}
        ending_nodes = set()

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_distance > distances[current_node.position]:
                continue
            
            end_of_movement = True

            for neighbor_pos in current_node.neighbors:

                if neighbor_pos in ignore_positions:
                    continue

                neighbor = map.navgraph.nodes[neighbor_pos]
                edge_cost = map.calculate_movement_cost(current_node.position, neighbor.position, self.size)
                
                if edge_cost is None:
                    continue

                distance = current_distance + edge_cost

                if self.speed.can_move(distance) and self.size <= neighbor.max_size:
                    end_of_movement = False
                    expended = current_distance + (self.speed - current_distance).get_min_move_cost(edge_cost)
                    if expended < distances[neighbor.position]:
                        distances[neighbor.position] = expended
                        previous[neighbor.position] = current_node
                        
                        heapq.heappush(queue, (expended, neighbor))

                        remaining_speed = self.speed.duplicate()
                        remaining_speed -= expended
                        reachable_nodes[neighbor_pos] = expended
            
            if end_of_movement and current_node.position not in ignore_positions:
                ending_nodes.add(current_node.position)
        
        paths = {}
        for node in map.navgraph.nodes:
            paths[node] = []
            previous_node = previous[node]
            while previous_node is not None:
                paths[node].insert(0, previous_node.position)
                previous_node = previous[previous_node.position]

        return reachable_nodes, paths, ending_nodes
    
    def get_movement_to(self, map, start_position, end_position):
        path_start_nodes = {start_position: None}
        paths = {}
        visitable_nodes = set()
        turn = 1

        while path_start_nodes:
            min_distance_node = None
            remaining_speed = None
            possible_path_endings = {}
            new_visitable_nodes = set()
            for path_start in path_start_nodes:
                reachable, _, path_endings = self.get_reachable_nodes(map, path_start, visitable_nodes)
                if end_position in reachable:
                    if min_distance_node is None or reachable[end_position] > remaining_speed:
                        min_distance_node = path_start
                        remaining_speed = reachable[end_position]
                new_visitable_nodes.update(reachable.keys())
                for path_end_position in path_endings:
                    possible_path_endings[path_end_position] = path_start
            
            if min_distance_node is None:
                paths.update(possible_path_endings)
                path_start_nodes = possible_path_endings
                visitable_nodes.update(new_visitable_nodes)
                turn += 1
            else:
                next_position = min_distance_node
                full_path = [min_distance_node, end_position]
                while next_position in paths and paths[next_position] in paths:
                    next_position = paths[next_position]
                    full_path.insert(0, next_position)
                return next_position, turn, full_path
        return None, -1, None
    
    def get_directed_push_to(self, map, start_position, toward_position, max_distance):
        line_nodes = map.get_tiles_in_line(start_position, toward_position)
        distance_remaining = max_distance
        path = []
        for i in range(len(line_nodes) - 1):
            move_start = line_nodes[i]
            move_end = line_nodes[i + 1]
            move_cost = map.calculate_movement_cost(move_start, move_end, self.size)

            if move_cost is None or move_cost.flying > distance_remaining:
                return path
            else:
                path.append(move_end)
                distance_remaining -= move_cost.flying
        return path

        