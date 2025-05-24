import time

from flask import Flask, request, jsonify,Response
from flask_cors import CORS
from robomaster import robot
from localization import distance_scan_script, plot
from localization import monte_carlo
from pathfinding import Map, Obstacle
from robot import RobotManager
import json
from pathfinding import *

app = Flask(__name__)
CORS(app, resources= {r"/*": {"origins": "*"}})

robot = RobotManager()
robot.start_stream()


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

@app.route("/send", methods=["GET"])
def receive_command():
    # data = request.get_json()
    # if not data or 'command' not in data:
    #     return jsonify({"error": "Invalid command format."}), 400
    # goal_id = data[]
    # seat = map.seats[goal_id]

    seat0 = robot.get_seats()[0]
    seat_coords = (seat0.x, seat0.y)

    start = (1,1)

    #path = graphMap.path_from_to(start, seat_coords)

    #path_instructions = graphMap.instructions_from_path(path)

    #map.plot_path(path)
    path_instructions = [(1, 1), (1, -1), (1, 0), (0, -1)]
    robot.resolve_path(path_instructions)

    print("Path instructions:", path_instructions)

    #print("Path", path)

    #json_dump = json.dumps(path_instructions, indent=4)

    return "test"

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
    return Response(robot.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



# MOVEMENT
@app.route('/random_dance')
def r_dance():
    robot.crazy_random_dance()
    return jsonify({"message": "Robot dances "}), 200
@app.route('/disco_dance')
def d_dance():
    robot.disco_dance()
    return jsonify({"message": "Robot dances"}), 200

@app.route('/wackel_dance')
def w_dance():
    robot.wackel_dance()
    return jsonify({"message": "Robot dances"}), 200

@app.route('/stop_audio')
def stop_audio():
    #might not work
    robot.stop_audio()
    robot.stop()
    return jsonify({"message": "Robot stops music"}), 200
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
@app.route('/stop_dance')
def stop_dance():
    robot.stop_audio()
    robot.set_speed(robot.speed_buff)
    robot.stop()
    return jsonify({"message":"Dance stopped"},200)
@app.route('/spin')
def spin_robot():
    robot.rotate_angle(720)
    return jsonify({"message": "Robot stopped"}), 200
# @app.route('/rotate_right_given_angle')
# def rotate_right():
#     robot.move('rotate_right')
#     return jsonify({"message": "Robot rotated right"}), 200



@app.route("/seats", methods=["GET"])
def get_seats():
    return jsonify(map.to_dict())


@app.route('/move_distance', methods=['POST'])
def move_distance():
    """
    Endpoint to move the robot a specified distance in a given direction.
    Expects JSON payload with 'direction' and 'distance'.
    'distance' in cm
    'direction" options:
        - "forward"
        - "backward"
        - "left"
        - "right"

    example payload:
    {
        "direction": "forward",
        "distance": 50
    }
    """
    data = request.get_json()
    direction = data.get("direction")
    distance = data.get("distance")

    if not direction or not isinstance(distance, (int, float)):
        return jsonify({"error": "Invalid input. Provide 'direction' and 'distance'."}), 400

    try:
        robot.move_distance(direction, distance)
        return jsonify({"message": f"Robot moved {distance} cm in {direction} direction."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rotate_angle', methods=['POST'])
def rotate_angle():
    """
    Endpoint to rotate the robot by a specified angle.
    Expects JSON payload with 'angle'.
        'angle' > 0 -> move right
        'angle < 0 -> move left

    example payload:
    {
        "angle": 90
    }
    """
    data = request.get_json()
    angle = data.get("angle")

    if not isinstance(angle, (int, float)):
        return jsonify({"error": "Invalid input. Provide 'angle' as a number."}), 400

    try:
        robot.rotate_angle(angle)
        return jsonify({"message": f"Robot rotated by {angle} degrees."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


