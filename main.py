from server import app
from robot import RobotManager
import time


if __name__ == "__main__":
    print("Starting server...")

    app.run(host='0.0.0.0' , port=8000)

    print("Server started.")



