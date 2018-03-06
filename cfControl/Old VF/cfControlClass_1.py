import numpy as np
import atexit
import zmq
import time
from pid import PID, PID_RP
import simplejson
from viconStream import viconStream

class cfControlClass():
    def __init__(self,name,savelog):
        #Communication
        self.context = zmq.Context()
        self.clientAddress = "tcp://127.0.0.1:1212"

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
                       zmq_connection='none')
        self.p_pid = PID_RP(name="pitch", P=self.pPID_P, I=self.pPID_I, D=self.pPID_D, Integrator_max=15, Integrator_min=-15, set_point=0,
                       zmq_connection='none')
        self.y_pid = PID_RP(name="yaw", P=self.yPID_P, I=self.yPID_I, D=self.yPID_D, Integrator_max=10, Integrator_min=-5, set_point=0,
                       zmq_connection='none')
        self.t_pid = PID_RP(name="thrust", P=self.tPID_P, I=self.tPID_I, D=self.tPID_D, set_point=0.5, Integrator_max=120,
                       Integrator_min=-0.01 / 0.035, zmq_connection='none')


        #UAV information
        self.name = name
        self.mode = 'none'
        self.x = []
        self.y = []
        self.z = []
        self.yaw = []




        #Settings
        self.update_rate = 0.01
        self.time_start = time.time()
        self.savelog = savelog

        self.startup()

    def startup(self):
        print('Connecting to ',self.clientAddress,' for ZMQ comd messages. . .')
        self.client_conn = self.context.socket(zmq.PUSH)
        self.client_conn.connect(self.clientAddress)
        print('Sending motor release command')
        time.sleep(1)

        print("Connecting to vicon stream. . .")
        self.cf_vicon = viconStream(self.name)
        time.sleep(2)

        print(self.cf_vicon.X["x"])

    def releaseMotors(self):
        self.cmd["ctrl"]["roll"] = 0
        self.cmd["ctrl"]["pitch"] = 0
        self.cmd["ctrl"]["yaw"] = 0
        self.cmd["ctrl"]["thrust"] = 0
        self.client_conn.send_json(self.cmd)
        print('Motor release cmd sent')


    def createLog(self):
        self.logName = 'log.txt'
        self.f = open(self.logName,"w+")

    def kill(self):
        #When program is killed, close the log file
        self.f.close()
        #Add landing functionality when killed if vehicle is in air


    def arm(self):
        #set throttle position to 0 and send message
        pass

    def takeoff(self,height):
        #Takeoff and hold height
        pass

    def land(self):
        #hover throttle position and slowly decrease z-setpoint
        pass
