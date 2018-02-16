from plots import responsePlots
import time
import numpy as np
import zmq


#Starting zmq listen
context = zmq.Context()
plot_conn = context.socket(zmq.PULL)

print('connecting')
plot_conn.bind("tcp://127.0.0.1:1515")
print('connected')

plot = responsePlots()

while True:

   # print('trying for data')
   try:
       pkt = plot_conn.recv_json()
       # print(pkt)

       # pkt = {
       #     "x": x,
       #     "y": y,
       #     "z": z,
       #     "yaw": y,
       #     "x_sp": 1,
       #     "y_sp": y,
       #     "z_sp": y,
       #     "yaw_sp": y,
       # }

       plot.update_plots(pkt)

   except:
       pass