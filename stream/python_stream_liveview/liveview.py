#!python3
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"[DEBUG] Current script directory (current_dir): {current_dir}")

decoder_path = os.path.abspath(os.path.join(current_dir, '..', 'decoder', 'output'))
# print(f"[DEBUG] Decoder path (Option 1 - Structure A): {decoder_path}")
# print(f"[DEBUG] Using decoder path: {decoder_path}")
# print(f"[DEBUG] Does this path exist? {os.path.exists(decoder_path)}")
# if os.path.exists(decoder_path):
#     print(f"[DEBUG] Contents of decoder path: {os.listdir(decoder_path)}")
# else:
#     print(f"[ERROR] The calculated decoder path does NOT exist. Please verify your directory structure.")

# # Add the chosen path to sys.path
sys.path.append(decoder_path)
#print(f"[DEBUG] sys.path now includes: {decoder_path}")
# --- End of Path Setup ---

import threading
import time
import numpy as np
import libh264decoder
import signal
from PIL import Image as PImage
import cv2
#import opus_decoder
#import pyaudio
import stream.python_stream_liveview.robot_connection as robot_connection
import enum
import queue


class ConnectionType(enum.Enum):
    WIFI_DIRECT = 1
    WIFI_NETWORKING = 2
    USB_DIRECT = 3


class RobotLiveview(object):
    WIFI_DIRECT_IP = '192.168.2.1'
    WIFI_NETWORKING_IP = '10.143.186.203'
    USB_DIRECT_IP = '192.168.42.2'

    def __init__(self, connection_type):
        self.connection = robot_connection.RobotConnection()
        self.connection_type = connection_type

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()

        self.video_decoder_thread = threading.Thread(target=self._video_decoder_task)
        self.video_decoder_msg_queue = queue.Queue(64)
        self.video_display_thread = threading.Thread(target=self._video_display_task)


        self.command_ack_list = []

        self.is_shutdown = True

    def open(self):
        if self.connection_type is ConnectionType.WIFI_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.WIFI_DIRECT_IP)
        elif self.connection_type is ConnectionType.USB_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.USB_DIRECT_IP)
        elif self.connection_type is ConnectionType.WIFI_NETWORKING:
            robot_ip = self.connection.get_robot_ip(timeout=10)
            if robot_ip:
                self.connection.update_robot_ip(robot_ip)
            else:
                print('Get robot failed')
                return False
        self.is_shutdown = not self.connection.open()

    def close(self):
        self.is_shutdown = True
        self.video_decoder_thread.join()
        self.video_display_thread.join()
        self.connection.close()

    def display(self):
        self.command('command')

        time.sleep(1)
        self.command('stream on')


        self.video_decoder_thread.start()
        self.video_display_thread.start()


        print('display!')

    def command(self, msg):
        # TODO: TO MAKE SendSync()
        #       CHECK THE ACK AND SEQ
        self.connection.send_data(msg)

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.video_decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, int(ls / 3), 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def _video_decoder_task(self):
        package_data = b''

        self.connection.start_video_recv()

        while not self.is_shutdown:
            buff = self.connection.recv_video_data()
            if buff:
                package_data += buff
                if len(buff) != 1460:
                    for frame in self._h264_decode(package_data):
                        try:
                            self.video_decoder_msg_queue.put(frame, timeout=2)
                        except Exception as e:
                            if self.is_shutdown:
                                break
                            print('video decoder queue full')
                            continue
                    package_data=b''

        self.connection.stop_video_recv()

    def _video_display_task(self):
        while not self.is_shutdown:
            try:
                frame = self.video_decoder_msg_queue.get(timeout=2)
            except Exception as e:
                if self.is_shutdown:
                    break
                print('video decoder queue empty')
                continue
            image = PImage.fromarray(frame)
            #img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # cv2.imshow("Liveview", image)
            cv2.waitKey(1)



def test():

    robot = RobotLiveview(ConnectionType.WIFI_DIRECT)

    def exit(signum, frame):
        robot.close()

    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)

    robot.open()
    robot.display()


if __name__ == '__main__':
    test()
