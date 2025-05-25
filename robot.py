
import keyboard
from robomaster import robot
import cv2
from pathfinding import *
import threading
import time
import random
import os

def get_random_wav_from_directory(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return None
    try:
        all_files = os.listdir(directory_path)
        wav_files = [f for f in all_files if f.lower().endswith(".wav")]
    except OSError as e:
        print(f"Error accessing directory {directory_path}: {e}")
        return None
    if not wav_files:
        print(f"Warning: No .wav files found in directory '{directory_path}'.")
        return None
    selected_file = random.choice(wav_files)
    return os.path.join(directory_path, selected_file)


class RobotManager:
    def __init__(self,  normal_speed=50, sprint_speed=100):
        self.ep_robot = robot.Robot()
        #self.ep_robot.initialize(conn_type="sta", sn="3JKCK6U0030AT6")
        self.ep_robot.initialize(conn_type="sta", sn="3JKCK7E0030BFN")

        seat0 = Seat(0, 1, 2)
        seat1 = Seat(1, 1, 1)
        o1 = Obstacle(10, 0, 4, 4)
        map = Map(22, 14, [o1], [])

        self.map = map
        self.ep_camera = self.ep_robot.camera
        self.ep_chassis = self.ep_robot.chassis
        self.normal_speed = normal_speed
        self.sprint_speed = sprint_speed
        self.current_speed = normal_speed
        self.speed_buff = self.current_speed
        self.running = True
        self.latest_frame = None
        self.current_angle = 0
        #self.capture_thread = threading.Thread(target=self._capture_frames)
        #self.capture_thread.daemon = True
        #self.lock = threading.Lock()
        self.start_stream()
        #self.capture_thread.start()

        print("Robot initialized.")


    def close_robot(self):
        if self.ep_robot:
            self.ep_robot.close()
            print("Robot closed.")


    def get_map(self):
        return self.map

    def get_seats(self):
        return self.map.seats

    def play_sound(self, sound):
        if self.ep_robot:
            self.ep_robot.play_sound(sound).wait_for_completed()
            print("Sound played.")

    def play_audio(self, audio_file):
        if self.ep_robot:
            self.ep_robot.play_audio(audio_file)
            print(f"Audio {audio_file} played.")

    def resolve_path_crabwalk(self, path_instructions):
        if not self.ep_robot:
            print("Robot not initialized.")
            return

        # for each path_instruction in path instructios
        for instruction in path_instructions:
            self.move_distance("forward",instruction[0] * 10)
            self.move_distance("left", instruction[1] * 10)

    def resolve_path(self, path_instructions):
        if not self.ep_robot:
            print("Robot not initialized.")
            return
        for instruction in path_instructions:
            dx, dy = instruction[0], instruction[1]

            if dx == 0 and dy == 0:
                target_angle = 0
            else:
                target_angle = -(math.degrees(math.atan2(dy, dx)) + 360) % 360
                if target_angle > 180:
                    target_angle -= 360  # Make angle negative if greater than 180
            self.rotate_angle(target_angle-self.current_angle)
            self.current_angle =  target_angle
            if dx + dy >= 2:
                self.move_distance("forward", 14.14 )
            else:
                self.move_distance("forward", 10)



    def get_robot(self):
        return self.ep_robot


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
                - "backward"
                - "left"
                - "right"
        """
        self.speed_buff = self.current_speed
        self.set_speed(50)
        self.move(direction)
        if direction == "forward":
            if dist < 0:
                dist = -dist
                direction = "backward"
        if direction == "backward":
            if dist < 0:
                dist = -dist
                direction = "forward"
        if direction == "left":
            if dist < 0:
                dist = -dist
                direction = "right"
        if direction == "right":
            if dist < 0:
                dist = -dist
                direction = "left"

        if direction == "backward":
            constant = 0.0367 #10cm
            # constant = 0.0355 #100cm
        elif direction == "right":
            constant = 0.041 #10cm
            
            # constant = 0.0376 #100cm
        elif direction == "left":
            constant = 0.04 #10cm
            
            # constant = 0.057 #100cm
        else:
            constant = 0.035 #10cm
            # constant = 0.04 #100cm
        time.sleep(constant * dist) #TODO change the sleep value
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
        constant = 0.0135
        self.current_angle += angle
        self.set_speed(50)
        if(angle > 0):
            self.move("rotate_right")
            time.sleep(constant * angle)
            self.stop()
        else:
            self.move("rotate_left")
            time.sleep(constant * -angle)
            self.stop()
        self.set_speed(self.speed_buff)

    def crazy_random_dance(self, moves=50):
        self.speed_buff = self.current_speed
        self.set_speed(100)

        possible_moves = [
            "forward", "forward_left", "forward_right",
            "left", "right", "rotate_left", "rotate_right"
        ]
        for _ in range(moves):
            move = random.choice(possible_moves)
            self.move(move)
            time.sleep(random.uniform(0.02, 0.25))
        self.stop()

        self.set_speed(self.speed_buff)


    def wave(self):
        self.play_audio("hello.wav")
        for x in range(2):
            if x == 1:
                audio_file_to_play = get_random_wav_from_directory("compliment_audio_greetings")
                self.play_audio(audio_file_to_play)
            self.move_arm("up", 70)
            #time.sleep(0.5)
            self.move_arm("down", 70)
            #time.sleep(0.5)

    def move(self, direction):
        """Move the robot in a specified direction.

        Args:
            direction (str): Direction to move. Options are:
                - "forward"
                - "forward_left"
                - "forward_right"
                - "backward_left"
                - "backward_right"
                - "left"
                - "right"
                - "rotate_left"
                - "rotate_right"
        """
        if direction == "forward":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=self.current_speed, w3=self.current_speed, w4=self.current_speed)
        elif direction == "backward":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=-self.current_speed, w3=-self.current_speed, w4=-self.current_speed)
        elif direction == "rotate_left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=-self.current_speed, w3=-self.current_speed, w4=self.current_speed)
        elif direction == "rotate_right":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=self.current_speed, w3=self.current_speed, w4=-self.current_speed)
        elif direction == "forward_left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=0, w3=self.current_speed, w4=0)
        elif direction == "forward_right":
            self.ep_chassis.drive_wheels(w1=0, w2=self.current_speed, w3=0, w4=self.current_speed)
        elif direction == "backward_left":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=0, w3=-self.current_speed, w4=0)
        elif direction == "backward_right":
            self.ep_chassis.drive_wheels(w1=0, w2=-self.current_speed, w3=0, w4=-self.current_speed)
        elif direction == "left":
            self.ep_chassis.drive_wheels(w1=self.current_speed, w2=-self.current_speed, w3=self.current_speed, w4=-self.current_speed)
        elif direction == "right":
            self.ep_chassis.drive_wheels(w1=-self.current_speed, w2=self.current_speed, w3=-self.current_speed, w4=self.current_speed)
        else:
            self.stop()

    def stop(self):
        """Stop the robot."""
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        
    #ARM MOVEMENT

    def move_arm(self, direction, distance):
        """Move the robotic arm in a specified direction.

        Args:
            direction (str): Direction to move. Options are:
                - "forward" (x+)
                - "backward" (x-)
                - "up" (y+)
                - "down" (y-)
            distance (int): Distance to move in millimeters.
        """
        if not self.ep_robot:
            print("Robot not initialized.")
            return

        if direction == "forward":
            self.ep_robot.robotic_arm.move(x=distance, y=0).wait_for_completed()
        elif direction == "backward":
            self.ep_robot.robotic_arm.move(x=-distance, y=0).wait_for_completed()
        elif direction == "up":
            self.ep_robot.robotic_arm.move(x=0, y=distance).wait_for_completed()
        elif direction == "down":
            self.ep_robot.robotic_arm.move(x=0, y=-distance).wait_for_completed()
        else:
            print(f"Invalid direction: {direction}")

    def stop_arm(self):
        """Stop the robotic arm."""
        if not self.ep_robot:
            print("Robot not initialized.")
            return

        self.ep_robot.robotic_arm.unsub_position()
        print("Robotic arm stopped.")

    def shutdown(self):
        """Shutdown the robot and close the connection."""
        self.stop()
        self.ep_robot.close()

    def start_stream(self):
        self.ep_camera.start_video_stream(display=False)
    def read_camera(self):
        return self.ep_camera.read_cv2_image()

    def _capture_frames(self):
        while self.running:
            frame = self.ep_camera.read_cv2_image()
            if frame is not None:
                with self.lock:
                    self.latest_frame = frame
            time.sleep(0.01)  # ~30 fps

    def generate_frames(self):
        while True:
            #with self.lock:
            #frame = self.latest_frame
            #if frame is None:
            frame = self.read_camera()
            #time.sleep(0.1)
            #continue
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                time.sleep(0.1)
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
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
    #         # Quit the program
    #         if keyboard.is_pressed('q'):
    #             print("Exiting...")
    #             self.running = False

    #         time.sleep(0.1)
    # finally:
    #     self.shutdown()
    
    def stop_audio(self):
        """Stop the currently playing audio."""
        if self.ep_robot:
            self.ep_robot.stop_audio()  # Replace with the actual method from your SDK
            print("Audio stopped.")
            
            
            
    def wackel_dance(self):
        if not self.ep_robot:
            print("Robot not initialized.")
            return

        self.speed_buff = self.current_speed
        self.set_speed(100)
        self.play_audio("wackelkontakt.wav")
        
        wackeltime = 0.04
        # self.move("rotate_right")
        # self.move_arm("down", 100)
        # time.sleep(wackeltime)

        self.move("rotate_left")
        self.move_arm("up", 50)
        time.sleep(wackeltime)
        

        self.move("rotate_right")
        self.move_arm("down", 50)
        time.sleep(wackeltime)

        self.move("rotate_left")
        self.move_arm("up", 50)
        time.sleep(wackeltime*5)
        

        self.move("rotate_right")
        self.move_arm("down", 50)
        time.sleep(wackeltime*50)
        
        self.move("rotate_left")
        self.move_arm("up", 50)
        time.sleep(wackeltime)

        self.move("rotate_right")
        self.move_arm("down", 50)
        time.sleep(wackeltime)
        
        self.move("rotate_left")
        self.move_arm("up", 50)
        time.sleep(wackeltime*5)
        
        self.move("rotate_right")
        self.move_arm("down", 50)
        time.sleep(wackeltime*10) 
        # self.stop_audio()
        self.set_speed(self.speed_buff)
        self.stop()
        print("Dance completed!")
    
            
    def disco_dance(self):
        if not self.ep_robot:
            print("Robot not initialized.")
            return

        self.speed_buff = self.current_speed
        self.set_speed(70)
        self.play_audio("disco2.wav")
        try:
            # Dance sequence
            for _ in range(2):  # Repeat the sequence 3 times
                # Forward-left while moving the arm up
                disco_time = 0.3
                self.move("forward_left")
                self.move_arm("up", 50)
                time.sleep(disco_time)
            
                # Forward-right while moving the arm down
                self.move("forward_right")
                self.move_arm("down", 50)
                time.sleep(disco_time)

                # Backward-left while moving the arm forward
                self.move("backward_left")
                self.move_arm("forward", 50)
                time.sleep(disco_time)

                # Backward-right while moving the arm backward
                self.move("backward_right")
                self.move_arm("backward", 50)
                time.sleep(disco_time)

                # Spin left while moving the arm up and down
                self.move("rotate_left")
                self.move_arm("up", 50)
                time.sleep(disco_time)
                self.move_arm("down", 50)
                time.sleep(disco_time)

                # Spin right while wiggling the arm
                self.move("rotate_right")
                self.move_arm("up", 30)
                time.sleep(0.3)
                self.move_arm("down", 30)
                time.sleep(0.3)

            # Final movement to return to the starting position
            self.move("backward_right")
            time.sleep(1)
            self.move("backward_left")
            time.sleep(1)

        finally:
            # Reset speed and stop the robot
            self.stop()
            # self.stop_audio()
            self.set_speed(self.speed_buff)
            print("Dance completed!")

