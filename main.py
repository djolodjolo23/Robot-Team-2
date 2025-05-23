from server import app
from robot import RobotManager


if __name__ == "__main__":
    robot = RobotManager()
    robot.initialize_robot()
    print("Starting server...")

    app.run(host='0.0.0.0' , port=8000)

    print("Server started.")

    #robot.play_sound()
    #robot.close_robot()


    # play sound


