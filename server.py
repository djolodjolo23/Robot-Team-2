import time

from flask import Flask, request, jsonify, Response
from robomaster import robot
from robot import RobotManager
from camera_stream import generate_frames
app = Flask(__name__)

robot = RobotManager()
robot.initialize_robot()

server_info = {
    "name": "Server",
    "status": "running",
    "message": "Server is running smoothly."
}

commands_demo = []

@app.route("/", methods=["GET"])
def home():
    return jsonify("Welcome to the server!"), 200

@app.route("/status", methods=["GET"])
def status():
    return jsonify(server_info), 200

@app.route("/send", methods=["POST"])
def receive_command():
    pass

@app.route("/sound", methods=["POST"])
def play_sound():
   # data = request.get_json()
    #sound_id = data.get("sound_id")
    sound_id = 1
    if sound_id:
        #.play_sound(sound_id).wait_for_completed()
        robot.play_sound(sound_id).wait_for_completed()
        return jsonify({"message": f"Sound {sound_id} played successfully."}), 200
    else:
        return jsonify({"error": "No sound ID provided."}), 400


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route("/seats", methods=["GET"])
def get_seats():
    seats = [
        {"seat_id": 1, "status": "available"},
        {"seat_id": 2, "status": "occupied"},
        {"seat_id": 3, "status": "available"}
    ]
    return jsonify(seats), 200