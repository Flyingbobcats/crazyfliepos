import numpy as np

# Decay functions
def VGauss(rrin):
    ovfR = 0.2
    ovfM = 0.6
    a = ovfR/np.sqrt(2*np.log(1/ovfM))
    G = np.exp(-(np.square(rrin))/(2*np.square(a)))

    return G

def VTanh(rrin):
    ovfR = 0.1
    ovfM = 0.5
    rrt = -(rrin)*2*np.pi+(2*ovfR)*np.pi
    G = 2*ovfM*(np.tanh((rrt)/2 + 0.5))

    return G