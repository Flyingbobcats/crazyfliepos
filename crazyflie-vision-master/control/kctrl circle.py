#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2015 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

"""
Kinect controller
"""

import sys
import os
import logging
import signal
import zmq
import math
import numpy as np

from pid import PID, PID_RP
import simplejson

# Roll/pitch limit
CAP = 15000.0
# Thrust limit
TH_CAP = 55000

YAW_CAP = 200

sp_x = 0
sp_y = 0
sp_z = 100

import zmq
import time

cmd = {
    "version": 1,
    "client_name": "N/A",
    "ctrl": {
        "roll": 0.1,
        "pitch": 0.1,
        "yaw": 0.0,
        "thrust": 0.0
    }
}

context = zmq.Context()
client_conn = context.socket(zmq.PUSH)
client_conn.connect("tcp://127.0.0.1:1212")

# kinect_conn = context.socket(zmq.PULL)
# kinect_conn.connect("tcp://192.168.0.2:7777")
# #kinect_conn.connect("tcp://172.16.12.136:1213")

midi_conn = context.socket(zmq.PULL)
midi_conn.connect("tcp://192.168.0.2:1250")

pid_viz_conn = context.socket(zmq.PUSH)
pid_viz_conn.connect("tcp://127.0.0.1:5123")

ctrl_conn = context.socket(zmq.PULL)
ctrl_conn.connect("tcp://127.0.0.1:1212")




#Connection to VICON

vicon_conn = context.socket(zmq.PULL)
vicon_conn.setsockopt(zmq.CONFLATE,1)
vicon_conn.setsockopt(zmq.LINGER,5)       #Socket timeout 0.5 seconds
result = vicon_conn.bind("tcp://127.0.0.1:7777")


yaw_sp = 0

#r_pid = PID_RP(name="roll", P=30, I=0, D=10, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
#p_pid = PID_RP(name="pitch", P=30, I=0, D=10, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
r_pid = PID_RP(name="roll", P=25, I=0.28, D=7, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
p_pid = PID_RP(name="pitch", P=25, I=0.28, D=7, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
y_pid = PID_RP(name="yaw", P=5, I=0, D=0.35, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
#r_pid = PID_RP(P=0.1, D=0.3, I=0, Integrator_max=5, Integrator_min=-5, set_point=0)
#p_pid = PID_RP(P=0.1, D=0.3, I=0, Integrator_max=5, Integrator_min=-5, set_point=0)
# t_pid = PID_RP(name="thrust", P=25, I=5*0.035, D=8*0.035, set_point=0.8, Integrator_max=0.01, Integrator_min=-0.01/0.035, zmq_connection=pid_viz_conn)

t_pid = PID_RP(name="thrust", P=25, I=5*0.035, D=800*0.035, set_point=1, Integrator_max=0.01, Integrator_min=-0.01/0.035, zmq_connection=pid_viz_conn)



# t_pid = PID_RP(name="thrust", P=20, I=.5, D=3, set_point=1, Integrator_max=0.01, Integrator_min=-0.01/0.035, zmq_connection=pid_viz_conn)

#y_pid = PID_RP(P=0.5, D=1.0, I=0.00025, set_point=300.0)

# Vertical position and velocity PID loops
# WORKING
v_pid = PID_RP(name="position", P=0.5, D=0.0, I=0.28, Integrator_max=100/0.035, Integrator_min=-100/0.035, set_point=1.6, zmq_connection=pid_viz_conn)
vv_pid = PID_RP(name="velocity", P=0.1, D=0.00315, I=0.28, Integrator_max=5/0.035, Integrator_min=-5/0.035, set_point=0, zmq_connection=pid_viz_conn)
#vv_pid = PID_RP(name="velocity", P=0.1, D=0.00315, I=0.28, Integrator_max=0.1/0.28, Integrator_min=-0.1/0.28, set_point=0, zmq_connection=pid_viz_conn)

#v_pid = PID_RP(name="position", P=0.2, D=0.0, I=0.01, Integrator_max=100, Integrator_min=-100, set_point=1.6, zmq_connection=pid_viz_conn)
#vv_pid = PID_RP(name="velocity", P=0.1, D=0.09, I=0.0, Integrator_max=5, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)

def waypoints(r_pid,y_pid,t_pid):
    X = 0
    Y = 0
    Z = 0
    drop = Z
    DT = time.time()- TimeStart
    if DT < 5:
        X = 0
        Y = 0
        Z = 1
        print("Waypoint 1")

    elif DT > 5 and DT<10:
        X = 1
        Y = 0
        Z = 1
        print("Waypoint 2")

    elif DT > 10:
        X = 1
        Y = 0
        Z = drop - 0.01
        print("Waypoint 3")

    # elif DT > 15 and DT< 20:
    #     X = 0
    #     Y = 0
    #     Z = 0



    r_pid.set_point = Y
    p_pid.set_point = X
    t_pid.set_point = Z

    return r_pid,y_pid,t_pid

f_x = 1000.0
f_y = f_x

MAX_THRUST = 65500

prev_z = 0
prev_t = time.time()

prev_vz = 0

dt = 0

midi_acc = 0

last_detect_ts = 0
detect_threas_ms = 1
on_detect_counter = 0

rp_p = r_pid.Kp
rp_i = r_pid.Ki
rp_d = r_pid.Kd

#Geofence
geo_travel = 2.5       #meters
geo_height = 1.75       #meters
geo_broken = False

hover_thrust = 60



#Send zero input message
print("Sending zero input message . . .")
cmd["ctrl"]["roll"] = 0
cmd["ctrl"]["pitch"] = 0
cmd["ctrl"]["thrust"] = 0
cmd["ctrl"]["yaw"] = 0
client_conn.send_json(cmd)  # , zmq.NOBLOCK)
print("Zero input message send . . .")
time.sleep(1)
detected = True
print("Starting to send control messages . . .")

TimeStart = time.time()

while detected == True:
    r_pid,y_pid,t_pid = waypoints(r_pid,y_pid,t_pid)
    try:
        try:
            position = vicon_conn.recv_json()
            if position["ext_pos"]["X"] is not False:
                x = position["ext_pos"]["X"] #meters
                y = position["ext_pos"]["Y"] #meters
                z = position["ext_pos"]["Z"] #meters
                angle = position["ext_pos"]["heading"] #radians
                detected = True

            else:
                print("No Vicon!!!")
                detected = False

            if abs(x)>geo_travel:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False
                geo_broken = True


            if abs(y) > geo_travel:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False
                geo_broken = True


            if abs(z) > geo_height:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False
                geo_broken = True


        except:
            print("Vicon error!!!!!")
            detect = 0

        # print("X:", "{0:.3f}".format(x), "\t", "Y:", "{0:.3f}".format(y), "\t", "z:", "{0:.3f}".format(z), "\t", "heading:", "{0:.3f}".format(np.rad2deg(angle)))


        if detected==True:
            last_detect_ts = time.time()

        #x_r = (x/f_x) * z
        #y_r = (y/f_y) * z

        # try:
        #     while True:
        #         md = midi_conn.recv_json(zmq.NOBLOCK)
        #         print (md["knobs"][0] - 0.5) * 2
        #         r_pid.set_point = (md["knobs"][0]-0.5) * 2
        #         p_pid.set_point = (md["knobs"][1]-0.5) * 2
        #         y_pid.set_point = md["knobs"][2] * 360
        #
        #         rp_p = md["sliders"][0] * 40
        #         rp_i = md["sliders"][1]
        #         rp_d = md["sliders"][2] * 200

                #r_pid.Kp = rp_p
                #p_pid.Kp = rp_p

                #r_pid.Ki = rp_i
                #p_pid.Ki = rp_i

                #r_pid.Kd = rp_d
                #p_pid.Kd = rp_d

                #midi_acc = (md["sliders"][3]-0.5)
        # except zmq.error.Again:
        #     pass

        # Get the set-points (if there are any)
        # try:
        #     while True:
        #         ctrl_sp = ctrl_conn.recv_json(zmq.NOBLOCK)
        #         yaw_sp = ctrl_sp["set-points"]["yaw"]
        #         r_pid.set_point = ctrl_sp["set-points"]["roll"]
        #         p_pid.set_point = ctrl_sp["set-points"]["pitch"]
        #         midi_acc = ctrl_sp["set-points"]["velocity"]
        # except zmq.error.Again:
        #     pass

        # print ("RP P/I/D={}/{}/{}".format(rp_p, rp_i, rp_d))

        if time.time() - last_detect_ts < detect_threas_ms and detected == True:
            if on_detect_counter >= 2:
                #print "IN  : x={:4.2f}, y={:4.2f}, z={:4.2f}, angle={:4.2f}".format(x, y, z, angle)
                #print "CORR: x={:4.2f}, y={:4.2f}, z={:4.2f}".format(x_r, y_r, z)

                safety = 10
                #roll = r_pid.update(sp_x-x)
                #pitch = p_pid.update(sp_z-z)
                #thrust = t_pid.update(sp_y-y)

                roll = r_pid.update(-y)
                pitch = p_pid.update(-x)
                thrust = t_pid.update(z)
                yaw = y_pid.update(((angle - yaw_sp + 360 + 180) % 360)-180)
                #print("Roll:", "{0:.3f}".format(roll), "\t","Pitch:", "{0:.3f}".format(pitch), "\t","Thrust:", "{0:.3f}".format(thrust))

                #Saturation control

                thrust = thrust+hover_thrust
                pitch_roll_cap = 30

                if thrust > 100:
                    thrust = 100

                elif thrust < 0:
                    thrust = 0

                if abs(pitch) > pitch_roll_cap:
                    pitch = np.sign(pitch)*pitch_roll_cap

                if abs(roll) > pitch_roll_cap:
                    roll = np.sign(roll)*pitch_roll_cap







                # roll_sp = roll
                # pitch_sp = pitch
                # yaw_out = yaw
                #thrust_sp = thrust+0.73

                # velocity = v_pid.update(z)
                # velocity = max(min(velocity, 10), -10)  #Limit vertical velocity between -1 and 1 m/sec
                # velocity = midi_acc
                # vv_pid.set_point = velocity
                # dt = (time.time() - prev_t)
                # curr_velocity = (z-prev_z)/dt
                # curr_acc = (curr_velocity-prev_vz)/dt
                # thrust_sp = vv_pid.update(curr_velocity) + 0.50
                # # print ("TH={:.2f}".format(thrust_sp))
                # #print "YAW={:.2f}".format(yaw)
                # prev_z = z
                # prev_vz = curr_velocity
                # prev_t = time.time()

                # thrust_sp = max(min(thrust_sp, 1), 0.40)

                #thrust_sp = max(min(thrust_sp, 0.90), 0.40)

                # if (yaw_out < -YAW_CAP):
                #     yaw_out = -YAW_CAP
                # if (yaw_out > YAW_CAP):
                #     yaw_out = YAW_CAP

                # pitch_corr = pitch_sp * math.cos(math.radians(-angle)) - roll_sp * math.sin(math.radians(-angle))
                # roll_corr = pitch_sp * math.sin(math.radians(-angle)) + roll_sp * math.cos(math.radians(-angle))

                #print "OUT: roll={:2.2f}, pitch={:2.2f}, thrust={:5.2f}, dt={:0.3f}, fps={:2.1f}".format(roll_corr, pitch_corr, thrust_sp, dt, 1/dt)
                # print ("OUT: alt={:1.4f}, thrust={:5.2f}, dt={:0.3f}, fps={:2.1f}, speed={:+0.4f}".format(z, thrust_sp, dt, 1/dt, curr_velocity))
                #print "dt={:0.3f}, fps={:2.1f}".format(dt, 1/dt)
                # cmd["ctrl"]["roll"] = roll_corr
                # cmd["ctrl"]["pitch"] = pitch_corr
                # cmd["ctrl"]["thrust"] = thrust_sp * 100
                # cmd["ctrl"]["yaw"] = yaw_out

                cmd["ctrl"]["roll"] = roll
                cmd["ctrl"]["pitch"] = -pitch
                cmd["ctrl"]["thrust"] = thrust
                cmd["ctrl"]["yaw"] = yaw

                # print("Roll:", "{0:.3f}".format(roll), "\t","Pitch:", "{0:.3f}".format(pitch), "\t","Thrust:", "{0:.3f}".format(thrust))

            else:
                 on_detect_counter += 1
        else:
            #print "No detect"
            cmd["ctrl"]["roll"] = 0
            cmd["ctrl"]["pitch"] = 0
            cmd["ctrl"]["thrust"] = 0
            cmd["ctrl"]["yaw"] = 0
            r_pid.reset_dt()
            p_pid.reset_dt()
            y_pid.reset_dt()
            v_pid.reset_dt()
            vv_pid.reset_dt()
            #v
            vv_pid.Integrator = 0.0
            r_pid.Integrator = 0.0
            p_pid.Integrator = 0.0
            y_pid.Integrator = 0.0
            on_detect_counter = 0

            print("Sending shutdown command to UAV")
            client_conn.send_json(cmd)
            break

        try:
            client_conn.send_json(cmd)#, zmq.NOBLOCK)
        except:
            print("NOBLOCK error")
    except simplejson.scanner.JSONDecodeError as e:
        print (e)

print("Program end")

