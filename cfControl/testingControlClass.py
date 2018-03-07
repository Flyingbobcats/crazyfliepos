from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('TRACKER_STICK',(False,'LandTest'),True)

while uav.active:
    time.sleep(60)
    uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

