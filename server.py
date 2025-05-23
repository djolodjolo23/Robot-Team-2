import time

from flask import Flask, request, jsonify
from robomaster import robot
from robot import RobotManager
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

@app.route("/sound", methods=["GET"])
def play_sound():
   # data = request.get_json()
    #sound_id = data.get("sound_id")
    sound_id = 1;
    if sound_id:
        #.play_sound(sound_id).wait_for_completed()
        robot.play_sound(sound_id).wait_for_completed()
        return jsonify({"message": f"Sound {sound_id} played successfully."}), 200
    else:
        return jsonify({"error": "No sound ID provided."}), 400
