from src.map.movement import MovementCost
import heapq

class NavNode:
    def __init__(self, position):
        self.position = position
        self.edges = []
        self.previous = None

    def add_edge(self, neighbor, costs):
        self.edges.append(NavEdge(neighbor, costs))

class NavEdge:
    def __init__(self, neighbor, costs):
        self.neighbor = neighbor
        self.costs = costs

class NavGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, position):
        if position in self.nodes:
            return
        node = NavNode(position)
        self.nodes[position] = node
        return node

    def add_edge(self, from_position, to_position, costs):
        if from_position not in self.nodes or to_position not in self.nodes:
            raise ValueError("Both nodes must exist before creating an edge.")
        self.nodes[from_position].add_edge(self.nodes[to_position], costs)

    def __str__(self):
        to_return = ""
        for node in self.nodes:
            to_return += str(node) + ": ["
            for edge in self.nodes[node].edges:
                to_return += str(edge.neighbor.position) + ", "
            if self.nodes[node].edges:
                to_return = to_return[:-2]
            to_return += "]\n"
        return to_return

class NavAgent:
    def __init__(self, speed):
        self.speed = speed

    def get_reachable_nodes(self, graph, start_position):
        start_node = graph.nodes[start_position]
        distances = {node: float('inf') for node in graph.nodes}
        previous = {node: None for node in graph.nodes}
        distances[start_node.position] = MovementCost(0)

        queue = [(MovementCost(0), start_node)]
        reachable_nodes = {start_node: self.speed}

        while queue:

            current_distance, current_node = heapq.heappop(queue)

            if current_distance > distances[current_node.position]:
                continue

            for edge in current_node.edges:
                neighbor = edge.neighbor
                distance = current_distance + edge.costs

                if distance < distances[neighbor.position] and self.speed.can_move(distance):
                    distances[neighbor.position] = distance
                    previous[neighbor.position] = current_node
                    heapq.heappush(queue, (distance, neighbor))

                for move_type in edge.costs.cost_types:
                    cost = getattr(edge.costs, move_type)
                    if cost is not None and getattr(self.speed - current_distance, self.speed.get_attribute_for(move_type)) >= cost:
                        remaining_speed = self.speed.duplicate()
                        remaining_speed.move(current_distance)
                        reachable_nodes[neighbor] = remaining_speed
        
        paths = {node: [] for node in graph.nodes}
        for node in graph.nodes:
            previous_node = previous[node]
            while previous_node is not None:
                paths[node].insert(0, previous_node.position)
                previous_node = previous[previous_node.position]

        return reachable_nodes, paths