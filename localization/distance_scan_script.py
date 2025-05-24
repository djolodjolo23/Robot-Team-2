def sub_data_handler(sub_info):
    global rotation_results
    distance = sub_info
    rotation_results.append(distance[0])
    
rotation_results=[]

#turns arround 360 degrees and collects distance data at frequency of 5Hz
def do_rotation_scan(ep_robot, frequency=5):
    global rotation_results
    rotation_results = []
    
    ep_sensor = ep_robot.sensor
    ep_sensor.sub_distance(freq=frequency, callback=sub_data_handler)
    ep_chassis = ep_robot.chassis
    
    for i in range(36):
        ep_chassis.move(x=0, y=0, z=10, xy_speed=5).wait_for_completed()
    ep_sensor.unsub_distance()
    return rotation_results