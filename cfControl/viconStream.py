import threading
import time
import viconClient
import numpy as np


class viconStream():
    def __init__(self, name):
        self.name = name
        self.X = {}
        self.X["x"] = []
        self.X["y"] = []
        self.X["z"] = []
        self.X["yaw"] = []
        self.X["yawRate"] = []

        self.update_rate = 0.01


        thread = threading.Thread(target=self.run, args=())
        self.lock = threading.Lock()
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        import time

        vc = viconClient.viconClient("192.168.0.197",801)
        vc.vicon_connect()
        print("Connected to vicon stream")
        time.sleep(1)
        print("starting to send position command!")


        X = vc.getPos(self.name)
        yaw_previous = X["yaw"]
        x_prev = X["x"]
        y_prev = X["y"]

        while True:
            # self.lock.acquire()
            x_prev = X["x"]
            y_prev = X["y"]
            yaw_previous = X["yaw"]
            X = vc.getPos(self.name)
            self.X["x"] = X["x"]
            self.X["y"] = X["y"]
            self.X["z"] = X["z"]
            self.X["yaw"] = X["yaw"]
            self.X["yawRate"] = (X["yaw"]-yaw_previous) / self.update_rate
            self.X["vx"] = (X["x"]-x_prev) / self.update_rate
            self.X["vy"] = (X["y"]-y_prev) / self.update_rate
            self.X["speed"] = np.sqrt(np.square(self.X["vx"])+np.square(self.X["vy"]))
            # self.lock.release()

            time.sleep(self.update_rate)









