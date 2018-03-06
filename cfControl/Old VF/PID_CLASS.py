import numpy as np
import zmq
import time
from pid import PID, PID_RP
import threading
import atexit




class PID_CLASS():
    def __init__(self):
        self.context = zmq.Context()
        self.client_conn = self.context.socket(zmq.PUSH)
        self.client_conn.connect("tcp://127.0.0.1:1212")

        atexit.register(self.kill)
        self.lock = threading.Lock()
        t = threading.Thread(target=self.run,args=())
        t.daemon = True
        t.start()


    def run(self):
        # Options
        self.dispControlMessage = True

        self.update_rate = 0.01
        self.SPx = 0
        self.SPy = 0
        self.SPz = 0
        self.SP_yaw = 0

        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0

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


        self.client_conn.send_json(self.cmd)

        time.sleep(1)
        #Controller gain default values
        self.rPID_P = 29
        self.rPID_I = 2.5
        self.rPID_D = 17
        self.rPID_set_point = 0

        self.pPID_P = 29
        self.pPID_I = 2.5
        self.pPID_D = 17
        self.pPID_set_point = 0

        self.yPID_P = 80
        self.yPID_I = 20
        self.yPID_D = 15

        self.tPID_P = 55
        self.tPID_I = 120
        self.tPID_D = 45
        self.tPID_set_point = 0

        #Setup PID controllers
        self.r_pid = PID_RP(name="roll", P=self.rPID_P, I=self.rPID_I, D=self.rPID_D, Integrator_max=15, Integrator_min=-15, set_point=0,
                       zmq_connection=0)
        self.p_pid = PID_RP(name="pitch", P=self.pPID_P, I=self.pPID_I, D=self.pPID_D, Integrator_max=15, Integrator_min=-15, set_point=0,
                       zmq_connection=0)
        self.y_pid = PID_RP(name="yaw", P=self.yPID_P, I=self.yPID_I, D=self.yPID_D, Integrator_max=10, Integrator_min=-5, set_point=0,
                       zmq_connection=0)
        self.t_pid = PID_RP(name="thrust", P=self.tPID_P, I=self.tPID_I, D=self.tPID_D, set_point=0.5, Integrator_max=120,
                       Integrator_min=-0.01 / 0.035, zmq_connection=0)

        while  True:
            time.sleep(self.update_rate)
            #Lock variables

            try:
                #Lock thread until calculations are completed
                self.lock.acquire()
                x = self.x
                y = self.y
                z = self.z
                yaw = self.yaw
                SPx = self.SPx
                SPy = self.SPy
                SPz = self.SPz
                self.lock.release()


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
                yaw_cmd = self.y_pid.update(0)

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

                self.client_conn.send_json(self.cmd)

                if self.dispControlMessage:
                    print("Roll:", "{0:.3f}".format(self.cmd["ctrl"]["roll"]), "\t","Pitch:", "{0:.3f}".format(self.cmd["ctrl"]["pitch"]), "\t","Yaw:", "{0:.3f}".format(self.cmd["ctrl"]["yaw"]), "\t","Thrust:", "{0:.3f}".format(self.cmd["ctrl"]["thrust"]))

                #Release thread so position so states can be updated

            except:
                #Cannot acquire lock
                pass

    def kill(self):
        print("Trying to send kill cmd. . .")
        sent = False
        while not sent:
            try:
                self.cmd["ctrl"]["roll"] = 0
                self.cmd["ctrl"]["pitch"] = 0
                self.cmd["ctrl"]["thrust"] = 0
                self.cmd["ctrl"]["yaw"] = 0
                self.client_conn.send_json(self.cmd)
                print("Kill cmd sent")
                sent = True
            except:
                pass


