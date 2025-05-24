import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse.csgraph as csg
import math
from matplotlib.patches import Rectangle
import random


class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def is_inside(self, x, y):
        """ Check if the point (x, y) is inside of the obstacle """
        
        return x >= self.x and x <= self.x + self.width and y >= self.y and y <= self.y + self.height
    
class Seat:
    """ Each seat is defined by a unique ID and its coordinates """
    def __init__(self, id, x: int, y: int):
        self.id = id
        self.x = x
        self.y = y

class Map:
    
    """Map defined by the grid [0, width - 1] x [0, heigth - 1]"""
    
    MAX_ITER      = 5000               # iterations for RRT*
    STEP_LEN      = 2.0                # incremental distance
    SEARCH_RAD    = 6.0                # radius for rewiring (RRT*)
    GOAL_RADIUS   = 3.0    
    
    def __init__(self, width, height, obstacles: list, seats: list):
        self.width = width
        self.height = height
        self.obstacles = obstacles
        self.seats = seats
        
    def get_seats(self):
        return self.seats
        
    def in_obstacle(self, x, y):
        for o in self.obstacles:
            if o.is_inside(x, y):
                return True
        return False
    
    def in_map(self, x, y):
        return x >= 0 and x <= self.width - 1 and y >= 0 and y <= self.height - 1
    
    def plot_map(self):
        
        fig, ax = plt.subplots(figsize=(7, 4))
        # Workspace outline
        ax.add_patch(Rectangle((0, 0), self.width, self.height,
                            linewidth=2, edgecolor="black", facecolor="skyblue", alpha = 0.2, label = 'office'))

        # Obstacles
        for i, o in enumerate(self.obstacles):
            ax.add_patch(Rectangle((o.x, o.y), o.width, o.height,
                                facecolor="red", edgecolor="red", alpha=0.6, label = 'obstacle' if i == 0 else '_nolegend_'))

        # Axes cosmetics
        min_dimension = np.min([self.width, self.height])
        ax.set_xlim(-1 * min_dimension * 0.05, self.width + min_dimension * 0.05)
        ax.set_ylim(-1 * min_dimension * 0.05, self.height + min_dimension * 0.05)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Workspace with Obstacles, Start, and Goal")
        plt.legend()
    
    def to_dict(self):
        """ Convert the map to a JSON serializable format """
        return {
            "width": self.width,
            "height": self.height,
            "obstacles": [{"x": o.x, "y": o.y, "width": o.width, "height": o.height} for o in self.obstacles],
            "seats": [{"id": s.id, "x": s.x, "y": s.y} for s in self.seats]
        }
        
class Node:
    __slots__ = ("x", "y", "parent", "cost")
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.parent = None
        self.cost = 0.0

    def point(self):
        return (self.x, self.y)
    
class RRT:
    
    def __init__(self, map, maxiter = 5000, step_len = 2.0, search_rad = 6.0, goal_rad = 3.0):
        self.map = map
        
        self.maxiter = maxiter
        self.step_len = step_len
        self.search_rad = search_rad
        self.goal_rad = goal_rad
    
    def distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])


    def segment_collision(self, p1, p2, step=0.5):
        """Returns True if the segment p1->p2 intersects any obstacle (rectangle)."""
        length = self.distance(p1, p2)
        steps = max(2, int(length / step))
        for i in range(steps + 1):
            t = i / steps
            x = p1[0] + t * (p2[0] - p1[0])
            y = p1[1] + t * (p2[1] - p1[1])
            for o in self.map.obstacles:
                if o.is_inside(x, y):
                    return True
        return False


    def random_point(self):
        return (random.uniform(0, self.width), random.uniform(0, self.height))


    def nearest(self, nodes, p):
        return min(nodes, key=lambda n: self.distance((n.x, n.y), p))


    def steer(self,from_p, to_p):
        d = self.distance(from_p, to_p)
        if d <= self.step_len:
            return to_p
        theta = math.atan2(to_p[1] - from_p[1], to_p[0] - from_p[0])
        return (from_p[0] + self.step_len * math.cos(theta),
                from_p[1] + self.step_len * math.sin(theta))


    def near_nodes(self, nodes, new_node):
        return [n for n in nodes if self.distance((n.x, n.y), (new_node.x, new_node.y)) <= self.search_rad]

    def rrt_star(self, start, goal):
        nodes = [Node(*start)]
        goal_node = None

        for _ in range(self.maxiter):
            rnd = self.random_point()
            nearest_node = self.nearest(nodes, rnd)
            new_point = self.steer(nearest_node.point(), rnd)

            if self.segment_collision(nearest_node.point(), new_point):
                continue  # skip if edge collides

            new_node = Node(*new_point)

            # Choose best parent among nearby nodes (cost + new edge)
            near = self.near_nodes(nodes, new_node)
            min_parent = nearest_node
            min_cost = nearest_node.cost + self.distance(nearest_node.point(), new_node.point())

            for n in near:
                if self.segment_collision(n.point(), new_node.point()):
                    continue
                c = n.cost + self.distance(n.point(), new_node.point())
                if c < min_cost:
                    min_cost = c
                    min_parent = n

            new_node.cost = min_cost
            new_node.parent = min_parent
            nodes.append(new_node)

            # Rewire nearby nodes through the new node if cheaper
            for n in near:
                if n is min_parent:
                    continue
                if self.segment_collision(n.point(), new_node.point()):
                    continue
                new_cost = new_node.cost + self.distance(n.point(), new_node.point())
                if new_cost < n.cost:
                    n.parent = new_node
                    n.cost = new_cost

            # Check for goal region
            if self.distance(new_node.point(), goal) <= self.goal_rad:
                if goal_node is None or new_node.cost < goal_node.cost:
                    goal_node = new_node

        if goal_node is None:
            return None, nodes  # failed to find a path

        # Construct path from goal_node back to start
        path = []
        n = goal_node
        while n is not None:
            path.append(n.point())
            n = n.parent
        path.reverse()
        return path, nodes

    
### Pathfinding by discretisizing the map into a graph ### 
    
class GraphMap:
    """Graph representation of the map for finding a path using dijkstra (or another graph shortest-path algorithm)"""
    def __init__(self, map: Map):
        # internal enumeration of nodes since adjacency matrix is |V|x|V|, can't be indexed by tuples
        nodes_to_coord = {}
        coord_to_nodes = {}
        i = 0
        for x in range(0, map.width):
            for y in range(0, map.height):
                    nodes_to_coord.update({i : (x, y)})
                    coord_to_nodes.update({(x, y) : i})
                    i = i + 1
        
        # Initialize adjacency matrix
        adjacency_matrix = np.zeros((map.width * map.height, map.width * map.height))
        
        for x in range(0, map.width):
            for y in range(0, map.height):
                orth_neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for (dx, dy) in orth_neighbors:
                    if not(map.in_obstacle(x, y)) and map.in_map(x + dx, y + dy) and not(map.in_obstacle(x + dx, y + dy)):
                        v = coord_to_nodes[(x, y)]
                        w = coord_to_nodes[(x + dx, y + dy)]
                        adjacency_matrix[v, w] = 1
                
                diag_neighbors = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                for (dx, dy) in diag_neighbors:
                    if not(map.in_obstacle(x, y)) and map.in_map(x + dx, y + dy) and not(map.in_obstacle(x + dx, y + dy)):
                        v = coord_to_nodes[(x, y)]
                        w = coord_to_nodes[(x + dx, y + dy)]
                        adjacency_matrix[v, w] = math.sqrt(2)
        
        self.nodes_to_coord = nodes_to_coord
        self.coord_to_nodes = coord_to_nodes
        self.graph = csg.csgraph_from_dense(adjacency_matrix)
        self.map = map
        
    def path_from_to(self, start, goal):
        start_index = self.coord_to_nodes[start]
        goal_index = self.coord_to_nodes[goal]
        
        dist, pred = csg.shortest_path(self.graph, directed = False, indices = start_index, return_predecessors = True)
        
        # no path found - should never happen if map is well defined
        if np.isinf(dist[goal_index]):
            raise ValueError(f"No connection from {start} to {goal}")
        
        path = []
        v = goal_index
        while v != start_index:
            path.append(v)
            v = pred[v]
            if v == -9999:
                raise ValueError("Broken predecessor chain – graph is disconnected.")
        path.append(start_index)
        path.reverse()
        
        path_in_coord = [self.nodes_to_coord[node] for node in path]
        
        return path_in_coord
    
    def instructions_from_path(self, path):
        instructions = []
        for i in range(1, len(path)):
            instructions.append(tuple(np.subtract(path[i], path[i - 1])))
        return instructions
        
    def plot_path(self, path):
        start = path[0]
        goal = path[-1]
        fig, ax = plt.subplots(figsize=(7, 4))

        # **Make room on the right for the legend
        fig.subplots_adjust(right=0.78)

        # Workspace outline
        ax.add_patch(Rectangle((0, 0), self.map.width, self.map.height,
                            linewidth=2, edgecolor="black", facecolor="skyblue", alpha = 0.2, label = 'office'))

        # Obstacles
        for i, o in enumerate(self.map.obstacles):
            ax.add_patch(Rectangle((o.x, o.y), o.width, o.height,
                                facecolor="red", edgecolor="red", alpha=0.6, label = 'obstacle' if i == 0 else '_nolegend_'))

        # plot the path
        xs, ys = zip(*path)
        ax.plot(xs, ys,
        linestyle='-',
        linewidth=2.5,
        color='orange',
        label='Path',
        zorder=2) 

        # Start & goal
        ax.scatter(*start, marker="o", s=100, label="Start", color = 'green')
        ax.scatter(*goal,  marker="X", s=100, label="Goal", color = 'purple')

        # Axes cosmetics
        ax.set_xlim(-1, self.map.width + 1)
        ax.set_ylim(-1, self.map.height + 1)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Office with Obstacles, Start, and Goal")

        # **Legend outside the grid**
        ax.legend(loc="upper left",            # anchor point inside the legend box
                bbox_to_anchor=(1.02, 1),    # (x, y) anchor just outside axes
                borderaxespad=0)

        plt.tight_layout()
        plt.show()
        
        
### End of pathfinding by discretisizing the map into a graph ###

# -------------------------- RUN & VISUALIZE -------------------------
# path, tree = rrt_star(START, GOAL, OBSTACLES)
# path.append(GOAL)

# fig, ax = plt.subplots(figsize=(6, 6))

# # Plot obstacles
# for (xmin, ymin, xmax, ymax) in OBSTACLES:
#     rect = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, alpha=0.3)
#     ax.add_patch(rect)

# # Plot RRT* tree
# for node in tree:
#     if node.parent is not None:
#         ax.plot([node.x, node.parent.x], [node.y, node.parent.y], linewidth=0.5)

# # Plot path if found
# if path:
#     xs, ys = zip(*path)
#     ax.plot(xs, ys, linewidth=3)

# # Plot start and goal
# ax.scatter([START[0]], [START[1]])
# ax.scatter([GOAL[0]], [GOAL[1]])

# ax.set_xlim(0, WIDTH)
# ax.set_ylim(0, HEIGHT)
# ax.set_aspect('equal')
# ax.set_title("RRT* Path Planning")
# plt.show()
