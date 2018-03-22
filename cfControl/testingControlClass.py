from cfControlClass import cfControlClass
import VectorField
import numpy as np
import DecayFunctions as df
import threading
import time

uav = cfControlClass('CF_1',(True,'ObsVF_1_20s'),True)

##
obs = cfControlClass('CF_obstacle',(False,'ObsVF_1_20s'),True)
# obs.ctrl.active = False
##

flighttime = 20
sleeptime = .2

# Create navigational field
cvf = VectorField.VField()
cvf.G = 1
cvf.H = 1
cvf.L = 0
cvf.radius = .5
cvf.xc = 0
cvf.yc = 0

##
ovf = VectorField.VField()
ovf.radius = 1
ovf.G = -1
ovf.H = 1
ovf.L = 0
ovf.xc = 0
ovf.yc = 1

if uav.active:
    X = uav.QueueList["vicon"].get()
    if abs(X["x"]) > .05 and abs(X["y"]) > .05:
        uav.takeoff(.3)
        time.sleep(5)
        uav.goto(0,0,.3)
        time.sleep(5)
        uav.goto(.05,0,.3)
        time.sleep(3)
    else:
        uav.takeoff(.3)
        time.sleep(5)


for i in range(0,int(flighttime/sleeptime)):
    X = uav.QueueList["vicon"].get()


    quadX = X["x"]
    quadY = X["y"]

    obsX = obs.QueueList["vicon"].get()
    ovf.xc = obsX["x"]
    ovf.yc = obsX["y"]

    newCVF = cvf.GetVF_at_XY(quadX,quadY)
    u = newCVF.F[0]
    v = newCVF.F[1]

    MAG = np.sqrt(np.square(u) + np.square(v))
    uNorm = u / MAG
    vNorm = v / MAG


    ##
    # Calculate obstacle field decay
    rOVF = np.sqrt(np.square(quadX - ovf.xc) + np.square(quadY - ovf.yc)) / 1
    p = df.ActualTanh(rOVF)

    # Obstacle field component
    newOVF = ovf.GetVF_at_XY(quadX,quadY)
    uAvoid = newOVF.F[0]
    vAvoid = newOVF.F[1]

    magAvoid = np.sqrt(np.square(uAvoid) + np.square(vAvoid))
    UAVOID = uAvoid / magAvoid
    VAVOID = vAvoid / magAvoid

    UAVOID = p * UAVOID
    VAVOID = p * VAVOID

    # Total field component
    uTotal = uNorm + UAVOID
    vTotal = vNorm + VAVOID

    MAG = np.sqrt(np.square(uTotal) + np.square(vTotal))
    u = uTotal / MAG
    v = vTotal / MAG
    ##

    d = .125
    headingCmd = np.arctan2(v, u)
    xCmd = d * np.cos(headingCmd) + X["x"]
    yCmd = d * np.sin(headingCmd) + X["y"]
    print(xCmd, yCmd)
    uav.goto(xCmd,yCmd,0.3)
    # time.sleep(5)
    # uav.goto(0,0,1)

    time.sleep(sleeptime)


uav.land()
time.sleep(2)
uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread
time.sleep(2)
print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

