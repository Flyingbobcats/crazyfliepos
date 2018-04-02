from cfControlClass import cfControlClass
import DecayFunctions as df
import numpy as np
import matplotlib.pyplot as plt
import VectorField

vfy = np.linspace(-1.5, 1.5, 45)
vfx = np.linspace(-1.5, 1.5, 45)

VF = VectorField.VField()
VF.isLine = True
VF.radius = .7
VF.G = 3
VF.H = 0
VF.xc = 0
VF.yc = 0
VF.endX = 1
VF.endY = 0

# obs = cfControlClass('CF_obstacle',(True,'obstacle_3222018_1353_20s'),True)
# obsX = obs.QueueList["vicon"].get()

OVF = VectorField.VField()
OVF.isLine = False
OVF.radius = .05
OVF.xc = .5
OVF.yc = 0
OVF.G = -1
OVF.H = 0



def calcVF(VF,OVF):
    XS = np.empty([len(vfx),len(vfy)])
    YS = np.empty([len(vfx),len(vfy)])
    US = np.empty([len(vfx),len(vfy)])
    VS = np.empty([len(vfx),len(vfy)])

    for i in range(0,len(vfx)):
        for j in range(0,len(vfy)):
            VF.calcVFatXY(vfx[i],vfy[j])
            OVF.calcVFatXY(vfx[i],vfy[j])

            XS[i][j] = vfx[i]
            YS[i][j] = vfy[j]

            u = VF.V[0]
            v = VF.V[1]

            # Calculate obstacle field decay
            # rOVF = np.sqrt(np.square(vfx[i] - OVF.xc) + np.square(vfy[j] - OVF.yc)) / OVF.radius
            rOVF = np.sqrt(np.square(vfx[i] - OVF.xc) + np.square(vfy[j] - OVF.yc)) / 1
            p = df.ActualTanh(rOVF)

            ou = OVF.V[0]
            ov = OVF.V[1]

            omag = np.sqrt(np.square(ou)+np.square(ov))
            ou = ou/omag
            ov = ov/omag

            print(p)
            ou = p * ou
            ov = p * ov

            mag = np.sqrt(np.square(u)+np.square(v))
            US[i][j] = u/mag
            VS[i][j] = v/mag

            U = u + ou
            V = v + ov
            #

            # U = ou
            # V = ov

            MAG = np.sqrt(np.square(U)+np.square(V))
            US[i][j] = U/MAG
            VS[i][j] = V/MAG




    XS = XS.tolist()
    YS = YS.tolist()
    US = US.tolist()
    VS = VS.tolist()

    return XS,YS,US,VS


theta = np.linspace(0,2*np.pi,30)
XS,YS,US,VS = calcVF(VF,OVF)
plt.quiver(XS,YS,US,VS,scale=50)
plt.plot([0,VF.endX],[0,VF.endY],color='r')
plt.plot(.3*np.cos(theta)+OVF.xc,.3*np.sin(theta)+OVF.yc)
plt.xlim(-2,2)
plt.ylim(-2,2)
plt.show()