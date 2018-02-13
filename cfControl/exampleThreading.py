import threading
import time
import numpy as np


class ThreadingExample(object):
    def __init__(self, interval=1):

        self.X = {}
        self.interval = interval


        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        from python_vicon import PyVicon

        while True:
            def vicon_connect():
                print("Connecting to Vicon...")
                client = PyVicon()
                client.connect("192.168.0.197", 801)

                if not client.isConnected():
                    print("Failed to connect to Vicon!")
                    return 1
                else:
                    print("Vicon connected!")
                    return client

            def getPos(name):
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

                            self.X["x"] = x_ENU
                            self.X["y"] = y_ENU
                            self.X["z"] = z_ENU
                            self.X["Yaw"] = heading

                            # print(X["x"], "\t", X["y"], "\t",X["z"])
                            # if s == quadName:
                            # print("X:", "{0:.3f}".format(x_ENU), "\t", "Y:", "{0:.3f}".format(y_ENU), "\t", "Z:",
                            #       "{0:.3f}".format(z_ENU), "\t", "Yaw:", "{0:.3f}".format(np.rad2deg(heading)))
                            print(self.X["x"])

                            # return X




            client = vicon_connect()
            print("Connected to vicon stream")
            time.sleep(1)

            print("starting to send position command!")
            getPos('CF_3')



example = ThreadingExample()
time.sleep(3)
print(example.X)
time.sleep(2)
print(example.X)
time.sleep(2)
print('Bye')