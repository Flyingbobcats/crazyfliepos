import numpy as np
import time

class fakeviconClient():
    def __init__(self,DeadPacket=False,Behavior='Static'):


        self.deadPacket = DeadPacket
        self.behavior = Behavior
        self.ts = time.time()

        self.x = 0.1
        self.y = 0
        self.z = 0
        self.angle = 0
        self.d_angle = np.deg2rad(5)

        self.r = 1


    def vicon_connect(self):
        print("Vicon connected!")

    def getPos(self,name):
        trans_scale = 1000
        X = {}
        while True:

            DT = time.time()-self.ts
            # if DT>5:
            #     self.deadPacket = True

            if self.deadPacket:
                # print('dead packet')
                x_ENU = False
                y_ENU = False
                z_ENU = False
                heading = False
                X["Yaw"] = heading
                X["x"] = x_ENU
                X["y"] = y_ENU
                X["z"] = z_ENU
                t2 = time.time()

                return X
            else:

                if self.behavior == 'Static':
                    x_ENU = self.x
                    y_ENU = self.y
                    z_ENU = self.z
                    heading = self.angle

                elif self.behavior=='circle':

                    self.angle = self.angle+self.d_angle
                    x_ENU = self.x+self.r*np.cos(self.angle)
                    y_ENU = self.y+self.r*np.sin(self.angle)
                    z_ENU = self.z
                    heading = self.angle


            if heading < 0:
                heading = heading + 2 * np.pi

            if heading > np.pi:
                heading = -(2 * np.pi - heading)

            X["x"] = x_ENU
            X["y"] = y_ENU
            X["z"] = z_ENU
            X["yaw"] = heading

            return X

