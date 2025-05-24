import time

from flask import Flask, request, jsonify #Response
from flask_cors import CORS
from robomaster import robot
from robot import RobotManager
#from camera_stream import generate_frames
from pathfinding import *
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

robot = RobotManager()

obstacle0 = Obstacle(10, 10, 20, 20)
obstacle1= Obstacle(40, 40, 20, 20)

seat0 = Seat(0, 90, 90)
seat1 = Seat(1, 1, 1)

map = Map(350, 230, [obstacle0,  obstacle1], [seat0, seat1])
seats = map.seats
obstacles = map.obstacles

#graphMap = GraphMap(map)

#print(jsonify(map))


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

# @app.route("/send_to_goal", methods=["POST"])
# def receive_command():
#     data = request.get_json()
#     if not data or 'goal' not in data:
#         return jsonify({"error": "Invalid command format. Expected JSON with 'goal' key."}), 400
#     #goal_id = data['goal']
#     #seat = map.seats[goal_id]
#
#     seat = seat0
#     seat_coords = (seat.x, seat.y)
#
#     start = (1, 1)
#
#     path = graphMap.path_from_to(start, seat_coords) # path
#
#     path_instructions = graphMap.instructions_from_path(path) # list of instructions
#



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


# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
#
#

# MOVEMENT
@app.route('/left')
def move_left():
    robot.move('left')
    return jsonify({"message": "Robot moved left"}), 200

@app.route('/right')
def move_right():
    robot.move('right')
    return jsonify({"message": "Robot moved right"}), 200

@app.route('/forward')
def move_forward():
    robot.move('forward')
    return jsonify({"message": "Robot moved forward"}), 200

@app.route('/backward')
def move_backward():
    robot.move('backward')
    return jsonify({"message": "Robot moved backward"}), 200

@app.route('/rotate_left')
def rotate_left():
    robot.move('rotate_left')
    return jsonify({"message": "Robot rotated left"}), 200

@app.route('/rotate_right')
def rotate_right():
    robot.move('rotate_right')
    return jsonify({"message": "Robot rotated right"}), 200

@app.route('/stop')
def stop_robot():
    robot.stop()
    return jsonify({"message": "Robot stopped"}), 200

@app.route("/seats", methods=["GET"])
def get_seats():
    return jsonify(map), 200


