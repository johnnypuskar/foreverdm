from src.stats.statistics import Speed
import heapq

class NavNode:
    def __init__(self, position):
        self.position = position
        self.edges = []

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
        distances[start_node] = 0

        queue = [(0, start_node)]
        reachable_nodes = {}

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_distance > distances[current_node]:
                continue

            for edge in current_node.edges:
                neighbor = edge.neighbor
                distance = current_distance + min(cost for cost in edge.costs.values() if cost is not None)

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(queue, (distance, neighbor))

                for move_type, cost in edge.costs.items():
                    if cost is not None and getattr(self.speed, move_type) >= cost:
                        remaining_speed = self.speed.duplicate()
                        remaining_speed.move(cost)
                        reachable_nodes[neighbor] = remaining_speed

        return reachable_nodes