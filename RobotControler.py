import keyboard
import time
from robomaster import robot

class RobotController:
    def __init__(self, normal_speed=50, sprint_speed=100):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="sta")
        self.ep_chassis = self.ep_robot.chassis
        self.normal_speed = normal_speed
        self.sprint_speed = sprint_speed
        self.current_speed = normal_speed
        self.running = False
        self.ep_robot.play_sound(robot.SOUND_ID_1F).wait_for_completed()

    def set_speed(self, speed_type):
        """Set the robot's speed.
        options: int in range (0, 100>
        string: "normal" - set speed to 50 (quite slow)
        string: "sprint" - set speed to 100 (max speed)
        """
        if isinstance(speed_type, int) and 0 < speed_type <= 100:
            self.current_speed = speed_type
        elif speed_type == "normal":
            self.current_speed = self.normal_speed
        elif speed_type == "sprint":
            self.current_speed = self.sprint_speed

    def move(self, direction):
        """Move the robot in a specified direction.`
        options:
        forward
        forward_left
        forward_right
        left
        right
        rotate_left
        rotate_right
        """
        if direction == "forward":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=self.current_speed, w3=self.current_speed, w4=self.current_speed)
        elif direction == "backward":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=-self.current_speed, w3=-self.current_speed, w4=-self.current_speed)
        elif direction == "left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=-self.current_speed, w3=-self.current_speed, w4=self.current_speed)
        elif direction == "right":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=self.current_speed, w3=self.current_speed, w4=-self.current_speed)
        elif direction == "forward_left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=0, w3=self.current_speed, w4=0)
        elif direction == "forward_right":
            self.ep_chassis.drive_wheels(w1=0, w2=self.current_speed, w3=0, w4=self.current_speed)
        elif direction == "rotate_left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=-self.current_speed, w3=self.current_speed, w4=-self.current_speed)
        elif direction == "rotate_right":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=self.current_speed, w3=-self.current_speed, w4=self.current_speed)
        else:
            self.stop()

    def stop(self):
        """Stop the robot."""
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def shutdown(self):
        """Shutdown the robot and close the connection."""
        self.stop()
        self.ep_robot.close()

    def run_keyboard_control(self):
        """Run the robot using keyboard controls. For local testing"""
        self.running = True
        print("Use W/A/S/D to move, Shift to sprint, Ctrl+A/D to rotate, and Q to quit.")
        try:
            while self.running:
                # Check for sprint
                if keyboard.is_pressed('shift'):
                    self.set_speed("sprint")
                else:
                    self.set_speed("normal")

                # Handle movement
                if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
                    self.move("forward_left")
                elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
                    self.move("forward_right")
                elif keyboard.is_pressed('w'):
                    self.move("forward")
                elif keyboard.is_pressed('s'):
                    self.move("backward")
                elif keyboard.is_pressed('d'):
                    self.move("right")
                elif keyboard.is_pressed('a'):
                    self.move("left")
                elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('a'):
                    self.move("rotate_left")
                elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('d'):
                    self.move("rotate_right")
                else:
                    self.stop()

                # Quit the program
                if keyboard.is_pressed('q'):
                    print("Exiting...")
                    self.running = False

                time.sleep(0.1)
        finally:
            self.shutdown()


if __name__ == "__main__":
    controller = RobotController()
    controller.run_keyboard_control()