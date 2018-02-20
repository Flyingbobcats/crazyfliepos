import numpy as np

# Decay functions
def VGauss(rrin):
    ovfR = 1
    ovfM = 1
    a = ovfR/np.sqrt(2*np.log(1/ovfM))
    G = np.exp(-(np.square(rrin))/(2*np.square(a)))

    return G

def VTanh(rrin):
    ovfR = 1
    ovfM = 1
    rrt = -(rrin)*2*np.pi+(2*ovfR)*np.pi
    G = -2*ovfM*(np.tanh((rrt)/2 + 0.5))

    return G


def ActualTanh(rrin):
    A = .5
    Ra = 1

    G = -((np.tanh(2*np.pi*rrin/Ra-np.pi))+1)/2 + 1

    return G