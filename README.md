# Ryan's Crazyflie control branch


# Crazyflie Position Guidance and Control

Python scripts for collecting vicon motion capture data and controlling crazyflie 2.0 quadcopter. 

# Instructions:

- Launch CFClient with ZMQ enabled
- Time based waypoint navigation can be achieved by executing kctrl_CoordinateTransform.py in cfControl folder

# kctrl_CoordinateTransform.py Explaination
kctrl_CoordinateTransform implements four PID controllers to produce roll, pitch, yaw, and thrust commands based on global x,y,z and heading set-points. A thread
is spawned that samples VICON data at 100Hz in the background that can be referenced by the controller. A log file is created at the termination of each run with each PID values and time of execution.

# Known problems and future improvements
- motor cuttoff is not guaranteed when geofence is breached
- motor cuttoff is not guaranteed when VICON recieves a dead packet
- Built in takeoff method
- Built in landing method
- Proximity waypoint switching (currently time based)
