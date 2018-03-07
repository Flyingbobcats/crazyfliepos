import threading
import numpy as np

class waypointManager():

    def __init__(self,name,QueueList):

        self.name = name
        # self.WPradius = WPradius
        self.QueueList = QueueList
        self.currentWP = 0
        self.sleep_rate = 0.05
        self.message = {}
        self.active = True
        self.sp = {}
        self.sp["x"] = []
        self.sp["y"] = []
        self.sp["z"] = []
        t = threading.Thread(target=self.run,args=())
        t.daemon = True
        t.start()


    def run(self):
        WPradius = .20
        L = 2 * WPradius + 10

        WPx = []
        WPy = []

        WPx.append(0)
        WPy.append(0)

        WPx.append(1)
        WPy.append(1)

        WPx.append(-1)
        WPy.append(1)

        WPx.append(-1)
        WPy.append(-1)

        WPx.append(1)
        WPy.append(-1)

        wptx = WPx[self.currentWP]
        wpty = WPy[self.currentWP]

        self.sp["x"] = wptx
        self.sp["y"] = wpty
        self.sp["z"] = 0
        self.QueueList["sp"].put(self.sp)

        while self.active:
            wptx = WPx[self.currentWP]
            wpty = WPy[self.currentWP]
            X = self.QueueList["vicon"].get()
            x = X["x"]
            y = X["y"]

            try:
                dx = wptx - x                   # change in x between the Waypoint and the UAV
                dy = wpty - y                   # change in y between the Waypoint and the UAV

                alpha = np.arctan2(dy, dx)      # angle between UAV and the current Waypoint measured from the x-axis

                A = x + L * np.cos(alpha)       # current x-position of the Dummy Point
                B = y + L * np.sin(alpha)       # current y-position of the Dummy point

                dA = wptx - A                   # change in x between the Waypoint and the Dummy Point
                dB = wpty - B                   # change in y between the Waypoint and the Dummy Point

                DUMMYtoWPT = np.sqrt(dA * dA + dB * dB) # calculate the distance between the Dummy Point and the Waypoint
                UAVtoWPT = np.sqrt(dx * dx + dy * dy)   # calculate the distance between the UAV and the Waypoint

                if DUMMYtoWPT >= UAVtoWPT:          # if the distance from the Dummy Point to the waypoint is greater than
                                                    # the distance from the UAV to the Waypoint...
                    if UAVtoWPT <= WPradius:   # ...and the distance from the UAV to the Waypoint is less than the specified radius
                        self.currentWP = self.currentWP + 1  # change to the next Waypoint
                        self.message["mess"] = 'WAYPOINT_REACHED'
                        self.message["data"] = self.name
                        self.QueueList["threadMessage"].put(self.message)
                        wptx = WPx[self.currentWP]
                        wpty = WPy[self.currentWP]
                        self.sp["x"] = wptx
                        self.sp["y"] = wpty
                        self.sp["z"] = 0
                        self.QueueList["sp"].put(self.sp)

            except:
                print("waypointManager exception met")