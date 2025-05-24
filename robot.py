import time

from robomaster import robot
import robomaster
from robomaster import conn
from MyQR import myqr
from PIL import Image

QRCODE_NAME = "qrcode.png"


class RobotManager:
    def __init__(self):
        self.ep_robot = None

    def initialize_robot(self):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="sta", sn="3JKCK7E0030BFN")
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
