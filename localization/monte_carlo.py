import random
import math

import matplotlib.pyplot as plt

from shapely.geometry import LineString, Polygon, Point

import numpy as np

 
class Particle:
    def __init__(self):
        self.probability = 0
        self.rotation = 0
        self.x = 0
        self.y = 0
        
    def copy(self):
        new_particle = Particle()
        new_particle.probability = self.probability
        new_particle.rotation = self.rotation
        new_particle.x = self.x
        new_particle.y = self.y
        return new_particle

class OccupationMap:
    def __init__(self, boundary_points=None, obstacles=None):
        # Outer wall (rectangle: xmin, ymin, xmax, ymax)
        self.boundary = Polygon(boundary_points) if boundary_points else Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        
        # List of obstacle polygons
        self.obstacles = [Polygon(obs) for obs in obstacles] if obstacles else []

    def distance_to_nearest_obstacle(self, x, y, r, max_distance=100.00):
        # Cast a ray from (x, y) in direction r
        ray_dx = math.cos(r)
        ray_dy = math.sin(r)
        end_x = x + max_distance * ray_dx
        end_y = y + max_distance * ray_dy
        ray = LineString([(x, y), (end_x, end_y)])

        # Check intersections with outer wall and all obstacles
        min_dist = max_distance
        all_polygons = [self.boundary] + self.obstacles
        for poly in all_polygons:
            intersection = ray.intersection(poly.boundary)
            if intersection.is_empty:
                continue
            if "Point" in intersection.geom_type:
                dist = Point(x, y).distance(intersection)
                min_dist = min(min_dist, dist)
            elif "MultiPoint" in intersection.geom_type:
                for pt in intersection.geoms:
                    dist = Point(x, y).distance(pt)
                    min_dist = min(min_dist, dist)
        return min_dist
    
    def get_particle_distance_scan(self,particle, num_steps):
        scan=[]
        for i in range(num_steps):
            scan.append(self.distance_to_nearest_obstacle(particle.x, particle.y, particle.rotation+i*2*math.pi/num_steps))
        return scan
    
    def in_obstacle(self, x, y):
        point = Point(x, y)
        return any(obs.contains(point) for obs in self.obstacles) or not self.boundary.contains(point)
    
    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 6))
        
        # Plot boundary
        x, y = self.boundary.exterior.xy
        ax.plot(x, y, color='black', linewidth=2, label='Boundary')

        # Plot obstacles
        for i, obs in enumerate(self.obstacles):
            x, y = obs.exterior.xy
            ax.fill(x, y, color='gray', alpha=0.7, label='Obstacle' if i == 0 else "")

        ax.set_aspect('equal')
        ax.set_xlim(-50, 150)
        ax.set_ylim(-50, 150)
        ax.grid(True)
        ax.set_title("Occupation Map")
        ax.legend()
    
    def get_dummy_scan(self, x, y, rotation, num_points=360):
        scan_data = []
        for i in range(num_points):
            angle = 2 * math.pi / num_points * i + rotation
            distance = self.distance_to_nearest_obstacle(x, y, angle)
            
            scan_data.append(distance)
        return scan_data
    
    def from_Map(map_obj):
        """ Convert a Map object to an OccupationMap """
        boundary_points = [(0, 0), (map_obj.width, 0), (map_obj.width, map_obj.height), (0, map_obj.height)]
        obstacles = []
        for obs in map_obj.obstacles:
            obstacles.append([(obs.x, obs.y), (obs.x + obs.width, obs.y), 
                              (obs.x + obs.width, obs.y + obs.height), (obs.x, obs.y + obs.height)])
        return OccupationMap(boundary_points=boundary_points, obstacles=obstacles)


class MonteCarloLocalization:
    def __init__(self, occ_map, num_particles=100):
        self.particles = []
        self.num_particles = num_particles
        self.occupation_map = occ_map
            
        self.init_particles()
        
    def init_particles(self):
        for i in range(self.num_particles):
            particle = Particle()
            particle.rotation = math.pi * random.uniform(0, 2)
            particle.x = random.uniform(0, 100)
            particle.y = random.uniform(0, 100)
            self.particles.append(particle)
            
    def update_particles(self, x, y, rotation):
        for particle in self.particles:
            particle.x += x
            particle.y += y
            particle.rotation = (particle.rotation+rotation)%  (2 * math.pi)  # Normalize rotation to [0, 2π)
    
        
  
    def update_particle_probabilities(self, scan_data):
        error=[]
        for particle in self.particles:
            particle_scan = self.occupation_map.get_particle_distance_scan(particle, len(scan_data))
            
            MSE_p = sum([(scan_data[i] - particle_scan[i])**2 for i in range(len(scan_data)) ])
            
            error.append(MSE_p)
        inverted_error = [1/(e + 1e-6) for e in error]  # Avoid division by zero
        sum_error = sum(inverted_error)

        for i in range(len(self.particles)):
            if self.occupation_map.in_obstacle(self.particles[i].x, self.particles[i].y):
                self.particles[i].probability = 0
            self.particles[i].probability = inverted_error[i] / sum_error if sum_error > 0 else 1
        
         
    def perturbate_particles(self, rotation, x, y, uniform=True):
        if uniform:
            for particle in self.particles:
                particle.rotation = (particle.rotation + random.uniform(-rotation, rotation)) % (2 * math.pi)  # Normalize rotation to [0, 2π)
                particle.x += random.uniform(-x, x)
                particle.y += random.uniform(-y, y)
        else:# Gaussian perturbation
            for particle in self.particles:
                particle.rotation =(particle.rotation + random.gauss(0, rotation)) % (2 * math.pi)  # Normalize rotation to [0, 2π)
                particle.x += random.gauss(0, x)
                particle.y += random.gauss(0, y)
            
    def resample_particles(self, next_particles=None):
        weights = [p.probability for p in self.particles]
        self.num_particles = next_particles if next_particles is not None else self.num_particles
        new_particles = []
        for i in range(self.num_particles):
            index = random.choices(range(len(self.particles)), weights)[0]
            new_particles.append(self.particles[index].copy())
        self.particles = new_particles
        
        
    def update_step(self, x,y,rot, scan_data, perturbation_parameters=(0.1, 1, 1), next_particles=None):
        self.update_particles(x, y, rot)
        self.perturbate_particles(*perturbation_parameters)
        self.update_particle_probabilities(scan_data)
        self.resample_particles(next_particles)
        