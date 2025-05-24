from flask import Flask, Response
import cv2
from stream.python_stream_liveview.liveview import RobotLiveview, ConnectionType  # Replace with actual import
from PIL import Image as PImage
import numpy as np

app = Flask(__name__)

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
        _, buffer = cv2.imencode('.jpg', img)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Robot Camera Feed</h1><img src="/video_feed" width="640"/>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
