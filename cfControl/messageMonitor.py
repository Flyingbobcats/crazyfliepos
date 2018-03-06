import threading
import time

class messageMonitor():
    def __init__(self,SleepRate = [],QueueList={}):

        self.sleep_rate = SleepRate
        self.QueueList = QueueList

        print('Starting message monitor')
        t = threading.Thread(target=self.run,args=())


    def run(self):

        time.sleep(1)
        while True:
            try:
                message = self.QueueList["threadMessage"].get(block=False)
                if message["mess"] == "VICON_CONNECTED":
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                elif message["mess"] == 'NO_INIT_VICON_DATA':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                elif message["mess"] == 'VICON_DATA_FULL':
                    print(message["mess"], '\t', "Queue size:", str(message["data"]))

                elif message["mess"] == 'DEAD_PACKET_EXCEEDS_LIMIT':
                    print(message["mess"], '\t', str(message["data"]))

                elif message["mess"] == 'VICON_DEACTIVATED':
                    print(message["mess"], '\t', str(message["data"]))

                # Control messages
                elif message["mess"] == 'MOTOR_UNLOCK_SENT':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                elif message["mess"] == 'VICON_QUEUE_EXCEPTION_ERROR':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))


                elif message["mess"] == 'NEW_SP_ACCEPTED':
                    print(message["mess"], '\t', "Position:", str(message["data"]))


                elif message["mess"] == 'ATTEMPTING_TO_SEND_KILL_CMD':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                elif message["mess"] == 'KILL_CMD_SENT':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))


                elif message["mess"] == 'THROTTLE_DOWN_START':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                elif message["mess"] == 'THROTTLE_DOWN_COMPLETE':
                    print(message["mess"], '\t', "Object Name:", str(message["data"]))

                else:
                    print(message)
            except:
                pass
            time.sleep(0.01)