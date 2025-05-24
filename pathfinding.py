import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse.csgraph as csg
import math
from matplotlib.patches import Rectangle


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
                            linewidth=2, edgecolor="black", facecolor="skyblue"))

        # Obstacles
        for o in self.obstacles:
            ax.add_patch(Rectangle((o.x, o.y), o.width, o.height,
                                facecolor="red", edgecolor="red", alpha=0.6))

        # Axes cosmetics
        ax.set_xlim(-1, self.width + 1)
        ax.set_ylim(-1, self.height + 1)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Workspace with Obstacles, Start, and Goal")
    
    
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

        xs, ys = zip(*path)           # unpack [(x1,y1), (x2,y2), …]
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