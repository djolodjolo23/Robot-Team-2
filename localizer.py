from localization import monte_carlo, distance_scan_script

from localization.monte_carlo import MonteCarloLocalization, OccupationMap

class Localizer:
    def __init__(self, ep_robot, Map, position=(1,1,0), num_particles=100, movement_perturbation=0.1, rotation_perturbation=0.1, perturbation_uniform=True, update_steps=0):
        
        self.ep_robot = ep_robot
        self.Map = Map
        self.mc = MonteCarloLocalization(Map, num_particles=num_particles)
        self.last_scan = None
        self.perturbation_param = (movement_perturbation, rotation_perturbation, perturbation_uniform)
        self.curr_position = position
        self.update_steps = update_steps
    
    def do_scan(self, frequency=5):
        scan=distance_scan_script.do_rotation_scan(self.ep_robot, frequency=frequency)
        return scan
    
    def step(self, dx, dy, drot, scan=None):
        if scan is None:
            scan = self.do_scan()
        self.mc.update_step(dx, dy, drot, scan, self.perturbation_param)
        for i in range(self.update_steps):
            self.mc.update_step(0, 0, 0, scan)
        return self.mc.max_particle()    
    
        