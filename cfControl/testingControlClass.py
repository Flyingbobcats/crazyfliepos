from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'LandTest'),True)
uav.printUpdateRate = False
while uav.active:

    time.sleep(1)

    print(uav.ctrl.active)
    print(uav.cf_vicon.active)
    if uav.ctrl.active == False and uav.cf_vicon.active == False:
        uav.active = False
        print(uav.active)
        time.sleep(1)


print('dead')

#Emtpy the Queues to properly shut down handler threads
for i in uav.QueueList:
    print("Emptying Queue: ", i)
    while not uav.QueueList[i].empty():
        uav.QueueList[i].get()


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

