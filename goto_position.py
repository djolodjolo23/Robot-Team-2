import localizer
from localization.monte_carlo import OccupationMap
import pathfinding
import math

class GotoPosition:
    def __init__(self, robot, map, start_position=(0, 0), localization_interval=5):
        self.robot = robot
        self.map=map
        self.occupation_map = OccupationMap.from_Map(self.map)
        self.graphMap = pathfinding.GraphMap(self.map)
        self.localizer = localizer.Localizer(robot, Map=self.occupation_map, position=start_position, num_particles=100, movement_perturbation=0.1, rotation_perturbation=0.1, perturbation_uniform=True, update_steps=0)
        self.current_position = start_position
        self.current_rotation = 0
        

    def goto(self, x, y):
        path = self.graphMap.path_from_to(self.current_position, (x,y))
        if path is None:
            print("No path found to the target position.")
            return False
        else:
            #repeat 3 steps until the robot is close enough to the target position
            while abs(self.current_position[0]-x)+abs(self.current_position[1]-y)  > 3:  
                
                #replan the whole path
                instructions = self.graphMap.instructions_from_path(path)
                
                #only perfrom the first n instructions to avoid too long paths
                instructions=instructions[:self.localization_interval]
                self.robot.resolve_instructions(instructions)
                
                #then do one localization step
                delta_x = sum([inst[0] for inst in instructions])
                delta_y = sum([inst[1] for inst in instructions])
                delta_rotation = self.curr_rotation- math.atan2(instructions[-1][1], instructions[-1][0])
                print("old_poition",self.current_position, (delta_x, delta_y, delta_rotation))
                x,y,r= self.localizer.step(delta_x, delta_y, delta_rotation)
                print("new_position", x, y, r)
                self.current_position = (x, y)
                self.current_rotation = r
                

        
        