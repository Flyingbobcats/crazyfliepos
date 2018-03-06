import numpy as np
import zmq
import time
from pid import PID_RP
import threading



class PID_CLASS():
    def __init__(self,QueueList = {},name = ''):

        self.time_start = time.time()
        self.name = name

        self.QueueList = QueueList

        self.context = zmq.Context()
        self.client_conn = self.context.socket(zmq.PUSH)
        self.client_conn.connect("tcp://127.0.0.1:1212")

        self.message = {}
        self.message["mess"] = None
        self.message["data"] = None

        t = threading.Thread(target=self.run,args=(QueueList,),name="PID")
        t.daemon = True
        t.start()


    def run(self,QueueList):
        # Options
        self.dispControlMessage = False

        self.sleep_rate = 0.0001
        self.update_rate = []

        self.cmd = {
            "version": 1,
            "client_name": "N/A",
            "ctrl": {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "thrust": 0.0
            }
        }

        if QueueList["controlShutdown"].empty():
            active = True
            self.SPx = 0
            self.SPy = 0
            self.SPz = 0
            self.SP_yaw = 0

            self.x = 0
            self.y = 0
            self.z = 0
            self.yaw = 0

            self.client_conn.send_json(self.cmd)

            self.message["mess"] = 'MOTOR_UNLOCK_SENT'
            self.message["data"] = self.name
            self.QueueList["threadMessage"].put(self.message)

            time.sleep(1)
            # Controller gain default values
            self.rPID_P = 29
            self.rPID_I = 2.5
            self.rPID_D = 15
            self.rPID_set_point = 0

            self.pPID_P = 29
            self.pPID_I = 2.5
            self.pPID_D = 15
            self.pPID_set_point = 0

            self.yPID_P = 80
            self.yPID_I = 20
            self.yPID_D = 15

            self.tPID_P = 45
            self.tPID_I = 120
            self.tPID_D = 45
            self.tPID_set_point = 0

            # Setup PID controllers
            self.r_pid = PID_RP(name="roll", P=self.rPID_P, I=self.rPID_I, D=self.rPID_D, Integrator_max=15,
                                Integrator_min=-15, set_point=0,
                                zmq_connection=0)
            self.p_pid = PID_RP(name="pitch", P=self.pPID_P, I=self.pPID_I, D=self.pPID_D, Integrator_max=15,
                                Integrator_min=-15, set_point=0,
                                zmq_connection=0)
            self.y_pid = PID_RP(name="yaw", P=self.yPID_P, I=self.yPID_I, D=self.yPID_D, Integrator_max=10,
                                Integrator_min=-5, set_point=0,
                                zmq_connection=0)
            self.t_pid = PID_RP(name="thrust", P=self.tPID_P, I=self.tPID_I, D=self.tPID_D, set_point=0,
                                Integrator_max=120,
                                Integrator_min=-120, zmq_connection=0)

            SPx = 0
            SPy = 0
            SPz = 0
            SP_yaw = 0

        else:
            active = False
            self.kill()

        for i in range(0,QueueList["vicon"].qsize()):
            #Clear vicon Q before starting
            QueueList["vicon"].get()


        while active:
            t1 = time.time()
            time.sleep(self.sleep_rate)
            try:
                if QueueList["vicon"].full():
                    pass

                try:
                    X = QueueList["vicon"].get(timeout=0.2)
                except:
                    self.message["mess"] = 'VICON_QUEUE_EXCEPTION_ERROR'
                    self.message["data"] = self.name
                    self.QueueList["threadMessage"].put(self.message)
                    self.kill()
                    return

                x = X["x"]
                y = X["y"]
                z = X["z"]
                yaw = X["yaw"]
                yawRate = X["yawRate"]


                if not QueueList["sp"].empty():
                    new_set_point = QueueList["sp"].get()

                    SPx = new_set_point["x"]
                    SPy = new_set_point["y"]
                    SPz = new_set_point["z"]

                    self.message["mess"] = 'NEW_SP_ACCEPTED'
                    self.message["data"] = new_set_point
                    self.QueueList["threadMessage"].put(self.message)


                    #Experimental, may cause unstable flight
                    self.r_pid.Integrator = 0
                    self.p_pid.Integrator = 0
                    # self.y_pid.Integrator = 0
                    # self.t_pid.Integrator = 0


                # Changing setpoint to local coordinates
                theta = np.arctan2(SPy - y, SPx - x)
                SPx_b = SPx - x
                SPy_b = SPy - y
                range_to_sp = np.sqrt(np.square(SPx_b) + np.square(SPy_b))
                xa = range_to_sp * np.cos(theta)
                ya = range_to_sp * np.sin(theta)

                # Calculate set point locations relative to the UAV frame
                xb = xa * np.cos(yaw) + ya * np.sin(yaw)
                yb = -xa * np.sin(yaw) + ya * np.cos(yaw)

                # Assign the relative set-point
                self.r_pid.set_point = xb - x
                self.p_pid.set_point = yb - y
                self.y_pid.set_point = self.SP_yaw - yaw
                self.t_pid.set_point = SPz


                #Update controller
                roll = self.r_pid.update(-x)
                pitch = self.p_pid.update(-y)
                thrust = self.t_pid.update(z)
                yaw_cmd = self.y_pid.update(yaw)

                # Saturation control
                pitch_roll_cap = 30
                if thrust > 100:
                    thrust = 100
                elif thrust < 0:
                    thrust = 0
                if abs(pitch) > pitch_roll_cap:
                    pitch = np.sign(pitch) * pitch_roll_cap
                if abs(roll) > pitch_roll_cap:
                    roll = np.sign(roll) * pitch_roll_cap

                #Lock variables, update message
                self.cmd["ctrl"]["roll"] = -roll
                self.cmd["ctrl"]["pitch"] = -pitch
                self.cmd["ctrl"]["thrust"] = thrust
                self.cmd["ctrl"]["yaw"] = -yaw_cmd


                self.client_conn.send_json(self.cmd,zmq.NOBLOCK)


                if self.dispControlMessage:
                    print("Roll:", "{0:.3f}".format(self.cmd["ctrl"]["roll"]), "\t","Pitch:", "{0:.3f}".format(self.cmd["ctrl"]["pitch"]), "\t","Yaw:", "{0:.3f}".format(self.cmd["ctrl"]["yaw"]), "\t","Thrust:", "{0:.3f}".format(self.cmd["ctrl"]["thrust"]))

                t2 = time.time()
                self.update_rate = 1 / (t2 - t1)

                #Log packet
                pkt = {
                    "time":time.time()-self.time_start,
                    "x": x,
                    "y": y,
                    "z": z,
                    "yaw": yaw,
                    "x_sp": SPx,
                    "y_sp": SPy,
                    "z_sp": SPz,
                    "yaw_sp": SP_yaw,
                }

                self.QueueList["dataLogger"].put_nowait(pkt)

                if not self.QueueList["controlShutdown"].empty():
                    if self.QueueList["controlShutdown"].get() == 'THROTTLE_DOWN':
                        self.throttleDown()
                        active = False
                    else:
                        self.kill()
                    return

                # if not logQ.full():
                #     logQ.put(pkt)
                # print(self.update_rate)
            except Exception as ex:
                print(ex)

    def kill(self):

        self.message["mess"] = 'ATTEMPTING_TO_SEND_KILL_CMD'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        self.sentKill = False
        while not self.sentKill:
            try:
                self.cmd["ctrl"]["roll"] = 0
                self.cmd["ctrl"]["pitch"] = 0
                self.cmd["ctrl"]["thrust"] = 0
                self.cmd["ctrl"]["yaw"] = 0


                self.client_conn.send_json(self.cmd,zmq.NOBLOCK)



                self.message["mess"] = 'KILL_CMD_SENT'
                self.message["data"] = self.name
                self.QueueList["threadMessage"].put(self.message)

                self.sentKill = True
            except:
                pass


    def throttleDown(self):

        self.message["mess"] = 'THROTTLE_DOWN_START'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)
        time.sleep(0.01)


        self.cmd["ctrl"]["roll"] = 0
        self.cmd["ctrl"]["pitch"] = 0
        self.cmd["ctrl"]["yaw"] = 0

        if self.cmd["ctrl"]["thrust"]>50:
            self.cmd["ctrl"]["thrust"] = 50

        while self.cmd["ctrl"]["thrust"] > 0:
            self.cmd["ctrl"]["thrust"] = self.cmd["ctrl"]["thrust"]-1
            self.client_conn.send_json(self.cmd, zmq.NOBLOCK)
            time.sleep(0.05)


        self.message["mess"] = 'THROTTLE_DOWN_COMPLETE'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        return

