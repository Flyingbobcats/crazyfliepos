from python_vicon import PyVicon
import numpy as np

class viconClient():
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port


    def vicon_connect(self):
        print("Connecting to Vicon...")
        client = PyVicon()
        client.connect(self.ip, self.port)

        if not client.isConnected():
            print("Failed to connect to Vicon!")
            return 1
        else:
            print("Vicon connected!")
            self.client = client
            return client

    def getPos(self,name):
        client = self.client
        client.frame()
        subjects = client.subjects()
        trans_scale = 1000
        X = {}
        while True:
            for s in subjects:
                if (s == name):
                    trans = client.translation(s)
                    if (trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0):
                        print('dead packet')
                        x_ENU = False
                        y_ENU = False
                        z_ENU = False
                        heading = False
                        X["Yaw"] = heading
                        X["x"] = x_ENU
                        X["y"] = y_ENU
                        X["z"] = z_ENU
                        return X
                    else:
                        rot = client.rotation(s)
                        x_ENU = trans[0] / trans_scale
                        y_ENU = trans[1] / trans_scale
                        z_ENU = trans[2] / trans_scale
                        heading = rot[2]

                    if heading < 0:
                        heading = heading + 2 * np.pi

                    if heading > np.pi:
                        heading = -(2 * np.pi - heading)

                    X["x"] = x_ENU
                    X["y"] = y_ENU
                    X["z"] = z_ENU
                    X["yaw"] = heading

                    # if s == quadName:
                    #     print("X:", "{0:.3f}".format(x_ENU), "\t", "Y:", "{0:.3f}".format(y_ENU), "\t", "Z:",
                    #           "{0:.3f}".format(z_ENU), "\t", "Yaw:", "{0:.3f}".format(np.rad2deg(heading)))


                    return X

