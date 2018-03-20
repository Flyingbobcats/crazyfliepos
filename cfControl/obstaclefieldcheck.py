from cfControlClass import cfControlClass
import VFControl as VectorField
import numpy as np
import DecayFunctions as df
import threading
import time
import matplotlib.pyplot as plt


obs = cfControlClass('CF_obstacle',(False,'ObsVF_1_20s'),True)
obsX = obs.QueueList["vicon"].get()

# Create navigational field
cvf = VectorField.CircleVectorField('Gradient')
cvf.G = 1
cvf.H = 1
cvf.L = 0
cvf.mCircleRadius = 1
cvf.xc = 0
cvf.yc = 0
cvf.bUsePathFunc = False
cvf.NormVFVectors = True

# Create obstacle field
ovf = VectorField.CircleVectorField('Gradient')
ovf.mCircleRadius = .0001
actualRadius = .05
ovf.G = -1
ovf.H = 1
ovf.L = 0
ovf.xc = obsX["x"]
ovf.yc = obsX["y"]
ovf.bUsePathFunc = False
ovf.bNormVFVectors = True
#endregion


def calcVF():
    vfy = np.linspace(-2,2,31)
    vfx = np.linspace(-2,2,31)

    ovf.xc = obsX["x"]
    ovf.yc = obsX["y"]

    XS = np.empty([len(vfx),len(vfy)])
    YS = np.empty([len(vfx),len(vfy)])
    US = np.empty([len(vfx),len(vfy)])
    VS = np.empty([len(vfx),len(vfy)])

    for i in range(0,len(vfx)):
        for j in range(0,len(vfy)):
            params = VectorField.VFData()
            params.x = vfx[i]
            params.y = vfy[j]

            rOVF = np.sqrt(np.square(vfx[i] - ovf.xc) + np.square(vfy[j] - ovf.yc))/actualRadius
            p = df.VLin(rOVF)

            newOVF = ovf.GetVF_at_XY(params)
            uAvoid =  newOVF.F[0]
            vAvoid =  newOVF.F[1]

            magAvoid = np.sqrt(np.square(uAvoid)+np.square(vAvoid))

            UAVOID = uAvoid / magAvoid
            VAVOID = vAvoid / magAvoid

            newCVF = cvf.GetVF_at_XY(params)
            cvfu = newCVF.F[0]
            cvfv = newCVF.F[1]

            mag = np.sqrt(np.square(cvfu)+np.square(cvfv))
            XS[i][j] = vfx[i]
            YS[i][j] = vfy[j]
            US[i][j] = cvfu / mag + UAVOID*p
            VS[i][j] = cvfv / mag + VAVOID*p

            MAG = np.sqrt(np.square(US[i][j])+np.square(VS[i][j]))
            US[i][j] = US[i][j]/MAG
            VS[i][j] = VS[i][j]/MAG


    XS = XS.tolist()
    YS = YS.tolist()
    US = US.tolist()
    VS = VS.tolist()

    return XS,YS,US,VS


XS,YS,US,VS = calcVF()
plt.scatter(ovf.xc,ovf.yc)
plt.quiver(XS,YS,US,YS,scale=20)
plt.xlim(-2,2)
plt.ylim(-2,2)
plt.show()