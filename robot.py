from robomaster import robot


class RobotManager:
    def __init__(self):
        self.ep_robot = None

    def initialize_robot(self):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="ap")
        print("Robot initialized.")

    def close_robot(self):
        if self.ep_robot:
            self.ep_robot.close()
            print("Robot closed.")

    def play_sound(self, sound):
        if self.ep_robot:
            self.ep_robot.play_sound(sound).wait_for_completed()
            print("Sound played.")


    def get_robot(self):
        return self.ep_robot
