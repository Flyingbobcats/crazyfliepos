import threading
import matplotlib.pyplot as plt
import numpy as np
import time

class responsePlots():
    def __init__(self,QueueList):

        self.QueueList = QueueList

        self.update_rate = 0.5
        self.plot_history_limit = 200

        self.x = np.array([])
        self.y = np.array([])
        self.z = np.array([])
        self.yaw = np.array([])
        self.x_sp = np.array([])
        self.y_sp = np.array([])
        self.z_sp = np.array([])
        self.yaw_sp = np.array([])

        #Entire histories
        self.xs = np.array([])
        self.ys = np.array([])
        self.zs = np.array([])
        self.yaws = np.array([])
        self.x_sps = np.array([])
        self.y_sps = np.array([])
        self.z_sps = np.array([])
        self.yaw_sps = np.array([])
        self.times = np.array([])

        #Limited histories
        self.XS = np.array([])
        self.YS = np.array([])
        self.ZS = np.array([])
        self.YAWS = np.array([])
        self.X_SPS = np.array([])
        self.Y_SPS = np.array([])
        self.Z_SPS = np.array([])
        self.YAW_SPS = np.array([])


        #Template for what pkt dictionaries should look like
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



        self.ts = time.time()


        #Start the thread
        self.update_plots()
        thread = threading.Thread(target=self.run,args=())
        thread.daemon = True
        thread.start()


    def update_plots(self):
        #Update the current states and setpoints

        try:
            pkt = self.QueueList["dataLogger"].get()
            print('getting plot data')


            self.x    = pkt["x"]
            self.y    = pkt["y"]
            self.z    = pkt["z"]
            self.yaw  = pkt["yaw"]
            self.x_sp = pkt["x_sp"]
            self.y_sp = pkt["y_sp"]
            self.z_sp = pkt["z_sp"]
            self.yaw_sp = pkt["yaw_sp"]
            self.time = time.time()-self.ts

            #Update histories
            self.xs      = np.append(self.xs,self.x)
            self.ys      = np.append(self.ys,self.y)
            self.zs      = np.append(self.zs,self.z)
            self.yaws    = np.append(self.yaws,self.yaw)
            self.x_sps   = np.append(self.x_sps,self.x_sp)
            self.y_sps   = np.append(self.y_sps,self.y_sp)
            self.z_sps   = np.append(self.z_sps,self.z_sp)
            self.yaw_sps = np.append(self.yaw_sps,self.yaw_sp)
            self.times = np.append(self.times,self.time)


            if len(self.xs)>=self.plot_history_limit:
                self.XS = self.xs[-self.plot_history_limit:]
                self.YS = self.ys[-self.plot_history_limit:]
                self.ZS = self.zs[-self.plot_history_limit:]
                self.YAWS = self.yaws[-self.plot_history_limit:]
                self.X_SPS = self.x_sps[-self.plot_history_limit:]
                self.Y_SPS = self.y_sps[-self.plot_history_limit:]
                self.Z_SPS =self.z_sps[-self.plot_history_limit:]
                self.YAW_SPS = self.yaw_sps[-self.plot_history_limit:]
                self.TIMES = self.times[-self.plot_history_limit:]


            else:
                self.XS = self.xs
                self.YS = self.ys
                self.ZS = self.zs
                self.YAWS = self.yaws
                self.X_SPS = self.x_sps
                self.Y_SPS = self.y_sps
                self.Z_SPS = self.z_sps
                self.YAW_SPS = self.yaw_sps
                self.TIMES = self.times
        except:
            print('plot error')




    def run(self):
        time.sleep(1)

        self.fig = plt.figure(figsize=(15,7.5))
        self.grid = plt.GridSpec(4,6,wspace=0.1,hspace=0.1)

        self.ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2)
        self.ax2 = plt.subplot2grid((4, 4), (1, 0), colspan=2)
        self.ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2)
        self.ax4 = plt.subplot2grid((4, 4), (3, 0), colspan=2)
        self.ax5 = plt.subplot2grid((4, 4), (0, 2), colspan=4,rowspan=4)
        plt.tight_layout()



        while True:
            try:
                self.update_plots()
                self.ax1.cla()
                self.ax1.plot(self.TIMES, self.XS, 'k.')
                self.ax1.plot(self.TIMES, self.X_SPS, 'r--')
                self.ax1.grid(True)
                self.ax1.set_ylabel('x (m)')
                self.ax1.set_ylim(-3,3)




                self.ax2.cla()
                self.ax2.plot(self.TIMES, self.YS, 'k.')
                self.ax2.plot(self.TIMES, self.Y_SPS, 'r--')
                self.ax2.grid(True)
                self.ax2.set_ylabel('y (m)')
                self.ax2.set_ylim(-3,3)


                self.ax3.cla()
                self.ax3.plot(self.TIMES, self.ZS, 'k.')
                self.ax3.plot(self.TIMES, self.Z_SPS, 'r--')
                self.ax3.grid(True)
                self.ax3.set_ylabel('z (m)')
                self.ax3.set_ylim(-3,3)


                self.ax4.cla()
                self.ax4.plot(self.TIMES, self.YAWS, 'k.')
                self.ax4.plot(self.TIMES, self.YAW_SPS, 'r--')
                self.ax4.grid(True)
                self.ax4.set_ylabel('yaw (degrees')



                #2D position in vicon area
                self.ax5.cla()
                self.ax5.plot(self.x, self.y, 'bo')
                self.ax5.plot(self.x_sp, self.y_sp, 'r*')
                self.ax5.grid(True)
                self.ax5.set_xlim(-3,3)
                self.ax5.set_ylim(-3,3)
                self.ax5.set_ylabel('y (m)')
                self.ax5.set_xlabel('x (m)')

                plt.pause(self.update_rate)

            except:
                pass


