from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'LandTest'),True)

while uav.active:

    time.sleep(5)
    uav.goto(1,1,1)
    time.sleep(5)
    uav.goto(0,0,0)





uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

