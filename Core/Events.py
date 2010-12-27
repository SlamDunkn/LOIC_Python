import threading, Queue
from collections import defaultdict

IRC_RECV = 1
LAZER_RECV = 2
START_LAZER = 3
IRC_RESTART = 4

class Event:

    def __init__(self, typeID, arg = None):
        self.typeID = typeID
        self.arg = arg


class EventManager(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__listeners = defaultdict(list)
        self.__queue = Queue.Queue(256)
        self.running = True

    def signalEvent(self, event):
        self.__queue.put(event)

    def addListener(self, typeid, listener):
        self.__listeners[typeid].append(listener)

    def run(self):
        while self.running:
            e = None
            try:
                e = self.__queue.get(True, 5)
            except:
                pass
            if e == None:
                continue
            for l in self.__listeners[e.typeID]:
                l(e)


    def stop(self):
        self.running = False
        

ev_Manager = None

def getEventManager():
    global ev_Manager
    if ev_Manager == None:
        ev_Manager = EventManager()
    return ev_Manager

