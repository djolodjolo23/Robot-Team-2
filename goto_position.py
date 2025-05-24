import localizer
from localization.monte_carlo import OccupationMap
import pathfinding
import math

class GotoPosition:
    def __init__(self, robot, start_position=(0, 0, 0), localization_interval=10):
        self.robot = robot
        self.map=robot.map
        self.occupation_map = OccupationMap.from_Map(self.map)
        self.graphMap = pathfinding.GraphMap(self.map)
        self.localizer = localizer.Localizer(robot.ep_robot, Map=self.occupation_map, position=start_position, num_particles=10, movement_perturbation=0, rotation_perturbation=0, perturbation_uniform=True, update_steps=0)
        self.current_position = start_position
        self.current_rotation = 0
        self.localization_interval = localization_interval
        

    def goto(self, x, y):
        path = self.graphMap.path_from_to(self.current_position, (x,y))

        if path is None:
            print("No path found to the target position.")
            return False
        else:
            #repeat 3 steps until the robot is close enough to the target position
            while abs(self.current_position[0]-x)+abs(self.current_position[1]-y) > 1:
                print("starting goto with path")
                #replan the whole path
                path = self.graphMap.path_from_to(self.current_position, (x, y))

                instructions = self.graphMap.instructions_from_path(path)


                #only perfrom the first n instructions to avoid too long paths
                instructions=instructions[:self.localization_interval]
                self.robot.resolve_path(instructions)
                
                #then do one localization step
                delta_x = sum([inst[0] for inst in instructions])
                delta_y = sum([inst[1] for inst in instructions])
                delta_rotation = self.current_rotation- math.atan2(instructions[-1][1], instructions[-1][0])
                print("old_poition",self.current_position, (delta_x, delta_y, delta_rotation))
                n_x,n_y,n_r= self.localizer.step(delta_x, delta_y, delta_rotation)

                print("new_position", n_x, n_y, n_r)
                self.current_position = (n_x, n_y)
                self.current_rotation = n_r
                

        
        