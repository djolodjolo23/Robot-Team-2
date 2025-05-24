import time
from robomaster import robot

DEFAULT_TIMEOUT_S = 5

ARM_X_RANGE = (100, 200)
ARM_Y_RANGE = (70, 150)
DEFAULT_ARM_X = 110
DEFAULT_ARM_Y = 100

def print_distances(sub_info):
    distance = sub_info
    sensor_1_cm = distance[0]/10
    print(f"[DISTANCE] SENSOR 1: {sensor_1_cm} cm")
def dance(ep_robot):
    for x in range(5):
        ep_robot.robotic_arm.moveto(x=DEFAULT_ARM_X,y=ARM_Y_RANGE[0]).wait_for_completed(timeout=DEFAULT_TIMEOUT_S)
        time.sleep(1)
        # ep_robot.robotic_arm.moveto(x=DEFAULT_ARM_X,y=DEFAULT_ARM_Y).wait_for_completed(timeout=DEFAULT_TIMEOUT_S)
        # time.sleep(1)
        ep_robot.robotic_arm.moveto(x=DEFAULT_ARM_X,y=ARM_Y_RANGE[1]).wait_for_completed(timeout=DEFAULT_TIMEOUT_S)
        time.sleep(1)
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')
    #version = ep_robot.get_version()
    #print(f"robot version: {version}")

    ep_robot.sensor.sub_distance(2,callback=print_distances)
    ep_robot.robotic_arm.moveto(x=DEFAULT_ARM_X,y=DEFAULT_ARM_Y).wait_for_completed(timeout=DEFAULT_TIMEOUT_S)
    time.sleep(1)
    dance(ep_robot)
    ep_robot.robotic_arm.moveto(x=DEFAULT_ARM_X,y=DEFAULT_ARM_Y).wait_for_completed(timeout=DEFAULT_TIMEOUT_S)
    time.sleep(1)
    ep_robot.sensor.unsub_distance()
    ep_robot.close()
