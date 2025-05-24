import time

from robomaster import robot
import robomaster
from robomaster import conn
from MyQR import myqr
from PIL import Image

QRCODE_NAME = "qrcode.png"


class RobotManager:
    def __init__(self,  normal_speed=50, sprint_speed=100):

        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="sta", sn="3JKCK7E0030BFN")
        self.ep_chassis = self.ep_robot.chassis
        self.normal_speed = normal_speed
        self.sprint_speed = sprint_speed
        self.current_speed = normal_speed
        self.speed_buff = self.current_speed
        self.running = False
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

    def connect_to_wifi(self, ssid, password):
        if self.ep_robot:
            helper = conn.ConnectionHelper()
            info = helper.build_qrcode_string(ssid=ssid, password=password)
            myqr.run(words=info)
            time.sleep(1)
            img = Image.open(QRCODE_NAME)
            img.show()
            if helper.wait_for_connection():
                print("Connected to WiFi!")
            else:
                print("Failed to connect to WiFi!")
                
                
                
    #MOVEMENT
    def set_speed(self, speed_type):
        """Set the robot's speed.

        Args:
            speed_type (int or str): 
                - int: A value in the range (0, 100].
                - "normal": Sets speed to the default normal speed (50).
                - "sprint": Sets speed to the default sprint speed (100).
        """
        if isinstance(speed_type, int) and 0 < speed_type <= 100:
            self.current_speed = speed_type
        elif speed_type == "normal":
            self.current_speed = self.normal_speed
        elif speed_type == "sprint":
            self.current_speed = self.sprint_speed

    def move_distance(self, direction, dist):
        """Move the robot in a specified direction.

        Args:
            dist (int): distance in cm;
            direction (str): Direction to move. Options are:
                - "forward"
                - "forward_left"
                - "forward_right"
                - "left"
                - "right"
        """
        self.speed_buff = self.current_speed
        self.set_speed(50)
        self.move(direction)
        time.sleep(0.05 * dist) #TODO change the sleep value
        self.stop()
        self.set_speed(self.speed_buff)
        
        
        
        
        
    def rotate_angle(self, angle):
        """Rotate the robot by a given angle.
        
            Args:
            angle(int): Angle in deg 
                angle > 0 -> turn right
                angle < 0 -> turn left 
        """
        self.speed_buff = self.current_speed
        self.set_speed(50)
        if(angle > 0):
            self.move("rotate_right")
            time.sleep(0.05 * angle) #TODO change the sleep value
            self.stop()
        else:
            self.move("rotate_left")
            time.sleep(0.05 * angle) #TODO change the sleep value
            self.stop()
        self.set_speed(self.speed_buff)
        
    def move(self, direction):
        """Move the robot in a specified direction.

        Args:
            direction (str): Direction to move. Options are:
                - "forward"
                - "forward_left"
                - "forward_right"
                - "left"
                - "right"
                - "rotate_left"
                - "rotate_right"
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

    # def run_keyboard_control(self):
    #     """Run the robot using keyboard controls. For local testing"""
    #     self.running = True
    #     print("Use W/A/S/D to move, Shift to sprint, Ctrl+A/D to rotate, and Q to quit.")
    #     try:
    #         while self.running:
    #             # Check for sprint
    #             if keyboard.is_pressed('shift'):
    #                 self.set_speed("sprint")
    #             else:
    #                 self.set_speed("normal")

    #             # Handle movement
    #             if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
    #                 self.move("forward_left")
    #             elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
    #                 self.move("forward_right")
    #             elif keyboard.is_pressed('w'):
    #                 self.move("forward")
    #             elif keyboard.is_pressed('s'):
    #                 self.move("backward")
    #             elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('a'):
    #                 self.move("rotate_left")
    #             elif keyboard.is_pressed('ctrl') and keyboard.is_pressed('d'):
    #                 self.move("rotate_right")
    #             elif keyboard.is_pressed('d'):
    #                 self.move("right")
    #             elif keyboard.is_pressed('a'):
    #                 self.move("left")
    #             else:
    #                 self.stop()

    #             # Quit the program
    #             if keyboard.is_pressed('q'):
    #                 print("Exiting...")
    #                 self.running = False

    #             time.sleep(0.1)
    #     finally:
    #         self.shutdown()

