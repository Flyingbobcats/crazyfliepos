
from PID_CLASS import PID_CLASS
import threading
import time
from viconStream import viconStream
import time


lock = threading.Lock()


cf_vicon = viconStream('CF_2')
time.sleep(3)


PID = PID_CLASS()
PID.dispControlMessage = True



count = 0
ts  = time.time()
z = 0.3
while True:

    dt = (time.time()-ts)
    time.sleep(0.005)



    x = cf_vicon.X["x"]
    y = cf_vicon.X["y"]
    z = cf_vicon.X["z"]


    PID.x = x
    PID.y = y
    PID.z = z



    if dt < 2:
        PID.SPx = 0
        PID.SPy = 0
        PID.SPz = 0

    elif dt ==2 or dt <5:
        PID.SPx = 0
        PID.SPy = 0
        PID.SPz = 0.3

    elif dt==5 or dt<10:

        z = z - 0.01
        PID.SPx = 0
        PID.SPy = 0
        PID.SPz = z

    else:
        PID.SPx = 0
        PID.SPy = 0
        PID.SPz = 0
        time.sleep(1)
        break

    # print(x,y,z)

