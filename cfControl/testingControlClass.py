from cfControlClass import cfControlClass
import VFControl as VectorField
import numpy as np
import DecayFunctions as df
import threading
import time

uav = cfControlClass('CF_3',(True,'LandTest'),True)


# Create navigational field
cvf = VectorField.CircleVectorField('Gradient')
cvf.G = 1
cvf.H = 1
cvf.L = 0
cvf.mCircleRadius = .5
cvf.xc = 0
cvf.yc = 0
cvf.bUsePathFunc = False
cvf.NormVFVectors = True

if uav.active:
    uav.takeoff(.3)
    time.sleep(5)

for i in range(0,100):
    X = uav.QueueList["vicon"].get()

    params = VectorField.VFData()
    params.x = X["x"]
    params.y = X["y"]

    newCVF = cvf.GetVF_at_XY(params)
    u = newCVF.F[0]
    v = newCVF.F[1]



    MAG = np.sqrt(np.square(u) + np.square(v))
    uNorm = u / MAG
    vNorm = v / MAG

    d = .125
    headingCmd = np.arctan2(v, u)
    xCmd = d * np.cos(headingCmd) + X["x"]
    yCmd = d * np.sin(headingCmd) + X["y"]
    print(xCmd, yCmd)
    uav.goto(xCmd,yCmd,0.5)
    # time.sleep(5)
    # uav.goto(0,0,1)
    time.sleep(.05)

uav.land()


uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

