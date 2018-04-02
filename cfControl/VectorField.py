import numpy as np

class VField():

    def __init__(self):
        self.x = 0
        self.y = 0
        self.xc = 0
        self.yc = 0
        self.endX = 0
        self.endY = 0
        self.xbar = 0
        self.ybar = 0
        self.A = 0
        self.B = []
        self.Vconv = []
        self.Vcirc = []
        self.V = [0,0,0]
        self.G = 1
        self.H = 1
        self.L = 0
        self.radius = 1
        self.normConv = True
        self.normCirc = not True
        self.normAll = True
        self.isLine = True

    def getXY(self,getx,gety):
        self.x = getx
        self.y = gety

    def calcBar(self):
        self.xbar = self.x - self.xc
        self.ybar = self.y - self.yc

    def calcAB(self):
        self.A = -1/(np.sqrt(np.square(np.square(self.xbar)) + np.square(np.square(self.ybar)) + (2*np.square(self.xbar)*np.square(self.ybar))
                             - (2*np.square(self.radius)*np.square(self.xbar)) - (2*np.square(self.radius)*np.square(self.ybar)) + np.square(self.radius)))

        self.B = [2*self.xbar*np.square(self.xbar) + 2*self.xbar*np.square(self.ybar) - 2*np.square(self.radius)*self.xbar,
                  2*self.ybar*np.square(self.ybar) + 2*self.ybar*np.square(self.xbar) - 2*np.square(self.radius)*self.ybar,
                  0]

    def calcVconv(self,getx,gety):
        self.getXY(getx,gety)
        self.calcBar()
        self.calcAB()
        self.Vconv = [x * self.A for x in self.B]

        if self.normCirc:
            mag = np.sqrt(np.square(self.Vconv[0])+np.square(self.Vconv[1]))

            for i in range(0,len(self.Vconv)):
                self.Vconv[i] = self.Vconv[i]/mag

    def calcVcirc(self):
        self.Vcirc = [2*self.ybar,
                      -2*self.xbar,
                      0]

        if self.normCirc:
            mag = np.sqrt(np.square(self.Vcirc[0])+np.square(self.Vcirc[1]))

            for i in range(0,len(self.Vcirc)):
                self.Vcirc[i] = self.Vcirc[i]/mag

    def calcVFatXY(self,getx,gety):
        if self.isLine:
            self.xc = self.endX
            self.yc = self.endY
            a = np.sin(np.arctan2(self.endY,self.endX))
            b = np.cos(np.arctan2(self.endY,self.endX))

            a1 = a * (getx - self.xc) + b * (gety - self.yc)
            ga1 = np.array([a, b, 0])
            a2 = 0
            ga2 = np.array([0, 0, 1])
            Vcnv = -self.G * (a1 * ga1 + a2 * ga2)
            Vcrc = np.cross(ga1, ga2)
            TV = [0, 0, 0]
            conv = Vcnv
            circ = Vcrc
            tv = TV
            self.V = conv + circ + tv

        else:
            self.calcVconv(getx,gety)
            self.calcVcirc()

            for i in range(0,len(self.V)):
                self.V[i] = self.G*self.Vconv[i] + self.H*self.Vcirc[i]



        if self.normAll:
            mag = np.sqrt(np.square(self.V[0]) + np.square(self.V[1]))
            for i in range(0,len(self.V)):
                self.V[i] = self.V[i] / mag