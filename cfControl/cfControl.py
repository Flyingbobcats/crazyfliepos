import numpy as np
import atexit
import zmq
import time
from pid import PID, PID_RP
import simplejson
from viconStream import viconStream


def savefile():
    f.close()
    print("File saved")

cmd = {
    "version": 1,
    "client_name": "N/A",
    "ctrl": {
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 0.0,
        "thrust": 0.0
    }
}


# def waypoints(wpt):
#     if wpt<=1:
#         x = 0
#         y = 0
#         z = 0
#         yaw = 0
#     elif wpt > 1 and wpt < 5:
#         x = 1
#         y = 0
#         z = 1
#         yaw = 0
#     elif wpt ==5 or wpt<6:
#         x = 0
#         y = 0
#         z = 0.4
#         yaw = 0
#     else:
#         x = 0
#         y = 0
#         z = -1
#         yaw = 0
#     return [x,y,z,yaw]


def waypoints(wpt):
    if wpt<=1:
        x = 0
        y = 0
        z = 0
        yaw = 0
    elif wpt > 1 and wpt < 5:
        x = 0
        y = 0
        z = 1
        yaw = 0

    elif wpt >= 5 and wpt < 7:
        x = -1
        y = 1
        z = 1
        yaw = 0

    elif wpt >= 7 and wpt < 9:
        x = -1
        y = -1
        z = 1
        yaw = 0

    elif wpt >= 9 and wpt < 11:
        x = 0
        y = 0
        z = 0.3
        yaw = 0


    elif wpt ==11 or wpt<12:
        x = 0
        y = 0
        z = 0.25
        yaw = 0
    else:
        x = 0
        y = 0
        z = -1
        yaw = 0
    return [x,y,z,yaw]

context = zmq.Context()
client_conn = context.socket(zmq.PUSH)
client_conn.connect("tcp://127.0.0.1:1212")

midi_conn = context.socket(zmq.PULL)
midi_conn.connect("tcp://192.168.0.2:1250")

pid_viz_conn = context.socket(zmq.PUSH)
pid_viz_conn.connect("tcp://127.0.0.1:5123")

ctrl_conn = context.socket(zmq.PULL)
ctrl_conn.connect("tcp://127.0.0.1:1212")

plot_conn = context.socket(zmq.PUSH)
plot_conn.connect("tcp://127.0.0.1:1515")



r_pid = PID_RP(name="roll", P=29, I=2.5, D=17, Integrator_max=15, Integrator_min=-15, set_point=0, zmq_connection=pid_viz_conn)
p_pid = PID_RP(name="pitch", P=29, I=2.5, D=17, Integrator_max=15, Integrator_min=-15, set_point=0, zmq_connection=pid_viz_conn)
y_pid = PID_RP(name="yaw", P=80, I=20, D=15, Integrator_max=10, Integrator_min=-5, set_point=0, zmq_connection=pid_viz_conn)
t_pid = PID_RP(name="thrust", P=55, I=120, D=45, set_point=0.5, Integrator_max=120, Integrator_min=-0.01/0.035, zmq_connection=pid_viz_conn)



prev_t = time.time()


last_detect_ts = 0
detect_threas_ms = 1
on_detect_counter = 0

rp_p = r_pid.Kp
rp_i = r_pid.Ki
rp_d = r_pid.Kd

#Geofence
geo_travel = 1.75       #meters
geo_height = 1.75      #meters


#Creating log
filename = "time"+" "+ str(time.localtime())+" "+"r_pid" +"_"+ str(int(r_pid.Kp)) + "_"+ str(int(r_pid.Ki))+"_"+ str(int(r_pid.Kd)) + '_' \
            +"p_pid" +"_"+ str(int(p_pid.Kp)) + "_"+ str(int(p_pid.Ki))+"_"+ str(int(p_pid.Kd)) + '_' \
            +"y_pid" +"_"+ str(int(y_pid.Kp)) + "_"+ str(int(y_pid.Ki))+"_"+ str(int(y_pid.Kd)) + ".txt"

atexit.register(savefile)
f = open(filename,"w+")

#Send zero input message
print("Sending zero input message . . .")
cmd["ctrl"]["roll"] = 0
cmd["ctrl"]["pitch"] = 0
cmd["ctrl"]["thrust"] = 0
cmd["ctrl"]["yaw"] = 0
client_conn.send_json(cmd)
print("Zero input message send . . .")
time.sleep(1)
detected = True
TimeStart = time.time()

print("Connecting to vicon stream. . .")
cf_vicon = viconStream('CF_3')
time.sleep(2)
print("Starting to send control messages . . .")



while detected == True:
    time.sleep(0.01)
    try:
        try:
            x = cf_vicon.X["x"]
            y = cf_vicon.X["y"]
            z = cf_vicon.X["z"]
            yaw = cf_vicon.X["yaw"]
            yaw_rate = cf_vicon.X["yawRate"]
            angle = yaw
            wpt = int((time.time()-TimeStart)/4)
            SPx,SPy,SPz,SP_yaw = waypoints(wpt)

            #Changing setpoint to local coordinates
            theta = np.arctan2(SPy - y,SPx-x)
            SPx_b = SPx-x
            SPy_b = SPy-y
            range_to_sp = np.sqrt(np.square(SPx_b)+np.square(SPy_b))
            xa = range_to_sp*np.cos(theta)
            ya = range_to_sp*np.sin(theta)

            #Calculate set point locations relative to the UAV frame
            xb = xa*np.cos(yaw)+ya*np.sin(yaw)
            yb = -xa*np.sin(yaw)+ya*np.cos(yaw)

            #Assign the relative set-point
            r_pid.set_point = xb-x
            p_pid.set_point = yb-y
            y_pid.set_point = SP_yaw - yaw
            t_pid.set_point = SPz



            if cf_vicon.X is not False:
                detected = True

            else:
                print("No Vicon!!!")
                detected = False

            if abs(x)>geo_travel:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False

            if abs(y) > geo_travel:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False

            if abs(z) > geo_height:
                print("Geofence breached at:","(","{0:.2f}".format(x),",","{0:.2f}".format(y),",","{0:.2f}".format(z),")")
                detected = False

        except:
            pass
            detect = 0

        # print("X:", "{0:.3f}".format(x), "\t", "Y:", "{0:.3f}".format(y), "\t", "z:", "{0:.3f}".format(z), "\t", "heading:", "{0:.3f}".format(np.rad2deg(angle)))

        if detected==True:
            last_detect_ts = time.time()

        if time.time() - last_detect_ts < detect_threas_ms and detected == True:
            if on_detect_counter >= 2:
                safety = 10
                roll = r_pid.update(-x)
                pitch = p_pid.update(-y)
                thrust = t_pid.update(z)
                yaw_cmd = y_pid.update(0)

                #Saturation control
                pitch_roll_cap = 30

                if thrust > 100:
                    thrust = 100

                elif thrust < 0:
                    thrust = 0

                if abs(pitch) > pitch_roll_cap:
                    pitch = np.sign(pitch)*pitch_roll_cap

                if abs(roll) > pitch_roll_cap:
                    roll = np.sign(roll)*pitch_roll_cap


                cmd["ctrl"]["roll"] =  -roll
                cmd["ctrl"]["pitch"] = -pitch
                cmd["ctrl"]["thrust"] = thrust
                cmd["ctrl"]["yaw"] = -yaw_cmd

                # print("Roll:", "{0:.3f}".format(cmd["ctrl"]["roll"]), "\t","Pitch:", "{0:.3f}".format(cmd["ctrl"]["pitch"]), "\t","Yaw:", "{0:.3f}".format(cmd["ctrl"]["yaw"]), "\t","Thrust:", "{0:.3f}".format(cmd["ctrl"]["thrust"]), "\t","Waypoint:", wpt)


                #Strings for logging
                time_str = str("Time:" +"\t"+ "{0:.3f}".format((time.time()-TimeStart)))
                r_set_point_str = str("\t"+"Roll Set Point:" +"\t"+ "{0:.3f}".format(r_pid.set_point))
                p_set_point_str = str("\t" + "Pitch Set Point:" +"\t"+ "{0:.3f}".format(p_pid.set_point))
                y_set_point_str = str("\t" + "Yaw Set Point:" +"\t"+ "{0:.3f}".format(y_pid.set_point))


                x_wp_str = str("\t" + "X_WP:" +"\t"+ "{0:.3f}".format(SPx))
                y_wp_str = str("\t" + "Y_WP:" +"\t"+ "{0:.3f}".format(SPy))
                z_wp_str = str("\t" + "Y_WP:" +"\t"+ "{0:.3f}".format(SPz))


                x_str = "\t"+"X:" +"\t"+ "{0:.3f}".format(x)
                y_str = "\t" + "Y:" +"\t"+ "{0:.3f}".format(y)
                z_str = "\t" + "Z:" +"\t"+ "{0:.3f}".format(z)
                heading_str = "\t" + "yaw:" +"\t"+ "{0:.3f}".format(np.rad2deg(angle))
                heading_rate = "\t" + "yaw rate:" +"\t"+ "{0:.3f}".format(np.rad2deg(yaw_rate))

                roll_str = str("\t"+"Roll:"+"\t"+"{0:.3f}".format(cmd["ctrl"]["roll"]))
                pitch_str = str("\t"+"Pitch:"+"\t"+"{0:.3f}".format(cmd["ctrl"]["pitch"]))
                yaw_str = str("\t" + "Yaw:" +"\t"+ "{0:.3f}".format(cmd["ctrl"]["yaw"]))
                thrust_str = str("\t"+"Thrust:"+"\t"+ "{0:.3f}".format(cmd["ctrl"]["thrust"]))+'\n'


                # control_data    = str("Roll:"+"{0:.3f}".format(cmd["ctrl"]["roll"]) , "\t"+"Pitch:"+str("{0:.3f}".format(cmd["ctrl"]["pitch"])), "\t","Thrust:", str("{0:.3f}".format(cmd["ctrl"]["thrust"])), "\t"+"Waypoint:", str(wpt))
                wp_data = x_wp_str+y_wp_str+z_wp_str
                set_point_data = r_set_point_str+p_set_point_str+y_set_point_str
                control_data = roll_str+pitch_str+yaw_str+thrust_str
                position_data   = x_str+y_str+z_str+heading_str+heading_rate

                f.write(time_str+set_point_data+wp_data+position_data+control_data)

                pkt = {
                    "x": x,
                    "y": y,
                    "z": z,
                    "yaw": yaw,
                    "x_sp": SPx,
                    "y_sp": SPy,
                    "z_sp": SPz,
                    "yaw_sp": SP_yaw,
                }

                # plot.update_plots(pkt)
                plot_conn.send_json(pkt)



            else:
                 on_detect_counter += 1
        else:
            print("Throttle down!!!!")
            for i in range(60,-5,-1):
                time.sleep(0.05)
                cmd["ctrl"]["roll"] = 0
                cmd["ctrl"]["pitch"] = 0
                cmd["ctrl"]["thrust"] = i
                cmd["ctrl"]["yaw"] = 0
                r_pid.reset_dt()
                p_pid.reset_dt()
                print("throttle = ",i)

                r_pid.Integrator = 0.0
                p_pid.Integrator = 0.0
                y_pid.Integrator = 0.0
                on_detect_counter = 0

                client_conn.send_json(cmd)
            break

        try:
            client_conn.send_json(cmd)#, zmq.NOBLOCK)
        except:
            print("NOBLOCK error")
    except simplejson.scanner.JSONDecodeError as e:
        print (e)

print("Program end")

