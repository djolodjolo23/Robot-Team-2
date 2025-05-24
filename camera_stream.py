from flask import Flask, Response
import cv2
from stream.python_stream_liveview.liveview import RobotLiveview, ConnectionType
from PIL import Image as PImage
import numpy as np


robot = RobotLiveview(ConnectionType.WIFI_NETWORKING)
robot.open()
robot.display()

# Start a background thread to keep the robot liveview running
# def keep_robot_alive():
#     while not robot.is_shutdown:
#         time.sleep(1)

#threading.Thread(target=keep_robot_alive, daemon=True).start()

def generate_frames():
    while True:
        try:
            frame = robot.video_decoder_msg_queue.get(timeout=2)
        except:
            continue
        image = PImage.fromarray(frame)
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', img,[int(cv2.IMWRITE_JPEG_QUALITY),95])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


