from cfControlClass import cfControlClass
import time

uav = cfControlClass('CF_1',(True,'LandTest'),True)
uav.displayMessageMonitor = False
uav.
uav.printUpdateRate = False
while uav.active:

    time.sleep(5)
    if uav.ctrl.active == False and uav.cf_vicon.active == False:
        uav.active = False
        time.sleep(1)



uav.shutdown()


