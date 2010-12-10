import socket, time
from Functions import *
from multiprocessing import Process

class TCPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket()
        self.socket.setblocking(1)

        self.flooder = flooder
        self.running = True
        self.byteCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

    def stop(self):
        self.running = False
        #print "adding", self.byteCount
        try:
            self.flooder.byteCount.put(self.byteCount, True, 5) #why the fuck does this not work when called by flooder?
        except:
            #print "failed to add"
            pass

    def run(self):
        try:
            while self.running:
                while self.running:
                    try:
                        self.socket.connect((self.flooder.host, self.flooder.port))
                        print "thread", self.id, "connected"
                        break
                    except Exception as e:
                        if e.args[0] == 106 or e.args[0] == 60:
                            break
                        print "Couldn't connect:", e.args, self.flooder.host, self.flooder.port
                        time.sleep(1)
                        continue
                    break

                while self.running:
                    try:
                        bytes = self.socket.send(self.message)
                        self.byteCount += bytes
                        if self.flooder.wait != None and self.flooder.wait != False:
                            time.sleep(self.flooder.wait)
                    except Exception as e:
                        if e.args[0] == 32 or e.args[0] == 104:
                            print "thread", self.id ,"connection broken, retrying."
                            self.socket = socket.socket()
                            break
                        print "Couldn't send message on thread", self.id, "because", e.args
                        time.sleep(0.1)
                        pass
        except KeyboardInterrupt:
            return
