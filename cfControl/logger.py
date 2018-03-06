import threading
import time
import atexit



class logger():
    def __init__(self,logName,QueueList):

        self.logName = logName
        self.QueueList = QueueList
        self.sleep_rate = 0.0001
        self.update_rate = []


        if self.logName is not 'Default':
            self.filename = self.logName + '.txt'
        else:
            self.filename = 'test.txt'


        self.f = open(self.filename, "w+")
        atexit.register(self.closeFile)

        thread = threading.Thread(target=self.run,args=(),name='dataLogger')
        thread.daemon = True
        thread.start()


    def closeFile(self):
        print('Closing file')
        self.f.close()

    def run(self):
        time.sleep(1)
        while True:
            t1 = time.time()
            if not self.QueueList["dataLogger"].empty():
                time.sleep(self.sleep_rate)
                data = self.QueueList["dataLogger"].get()
                line = str(data)+'\n'
                self.f.write(line)
                t2 = time.time()
                self.update_rate=1/(t2-t1)
                # print(self.update_rate)

