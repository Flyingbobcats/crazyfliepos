import threading
import time
import viconClient

from utilities import fakeviconClient


class viconStream():
    # def __init__(self, name,q,error_queue):
    def __init__(self, name,QueueList):

        self.name = name
        self.DeadPacketCount = 0
        self.MaxDeadPackets = 20


        #active will be switched to false by the system monitor
        self.active = True


        self.X = {}
        self.X["x"] = []
        self.X["y"] = []
        self.X["z"] = []
        self.X["yaw"] = []
        self.X["yawRate"] = []

        self.message = {}
        self.message["mess"] = None
        self.message["data"] = None

        self.sleep_rate = 0.005
        self.update_rate = []

        thread = threading.Thread(target=self.run, args=(QueueList,),name="VICON")
        thread.daemon = True
        thread.start()

    def run(self,QueueList):
        #Switch comments to use fake vicon data
        vc = viconClient.viconClient("192.168.0.197",801)
        #vc = fakeviconClient.fakeviconClient()
        vc.vicon_connect()



        time.sleep(1)

        self.message["mess"] = 'VICON_CONNECTED'
        self.message["data"] = self.name
        QueueList["threadMessage"].put(self.message)
        time.sleep(0.00001)

        try:
            X = vc.getPos(self.name)
            self.yp = X["yaw"]

        except KeyError:
            self.message["mess"] = 'NO_INIT_VICON_DATA'
            self.message["data"] = self.name
            QueueList["threadMessage"].put(self.message)
            time.sleep(0.00001)
            return

        while self.active:
            t1 = time.time()
            X = vc.getPos(self.name)


            if X["x"] is not False:
                self.X["x"] = X["x"]
                self.X["y"] = X["y"]
                self.X["z"] = X["z"]
                self.X["yaw"] = X["yaw"]
                self.X["yawRate"] = (X["yaw"]-self.yp) / self.sleep_rate

                self.yp = X["yaw"]
                self.DeadPacketCount = 0

                if QueueList["vicon"].full():
                    self.message["mess"] = 'VICON_DATA_FULL'
                    self.message["data"] = str(QueueList["vicon"].qsize())
                    QueueList["threadMessage"].put(self.message)
                    time.sleep(0.0001)
                else:
                    QueueList["vicon"].put(self.X)

            else:
                self.DeadPacketCount = self.DeadPacketCount + 1
                if self.DeadPacketCount >= self.MaxDeadPackets:
                    self.message["mess"] = 'DEAD_PACKET_EXCEEDS_LIMIT'
                    self.message["data"] = str(self.DeadPacketCount) + ' Packets lost for :' + self.name
                    QueueList["threadMessage"].put(self.message)


            time.sleep(self.sleep_rate)
            t2 = time.time()

            self.update_rate = 1 / (t2 - t1)


        if not self.active:
            self.message["mess"] = 'VICON_DEACTIVATED'
            self.message["data"] = self.name
            QueueList["threadMessage"].put(self.message)
            return














