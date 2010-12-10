import threading, Queue

IRC_RECV = 1
LAZER_RECV = 2
START_LAZER = 3
IRC_RESTART = 4

class Event:

    def __init__(self, typeID, arg = None):
        self.typeID = typeID
        self.arg = arg

class Listener:

    def __init__(self, typeID, function):
        self.typeID = typeID
        self.function = function

class EventManager(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__eventStack = []
        self.__listeners = []
        self.__queue = Queue.Queue(256)
        self.running = True

    def signalEvent(self, event):
        self.__queue.put(event)

    def addListener(self, listener):
        self.__listeners.append(listener)

    def run(self):
        while self.running:
            e = None
            try:
                e = self.__queue.get(True, 5)
            except:
                pass
            if e == None:
                continue

            for l in self.__listeners:
                if l.typeID == e.typeID:
                    l.function(e)


    def stop(self):
        self.running = False
        

ev_Manager = None

def getEventManager():
    global ev_Manager
    if ev_Manager == None:
        ev_Manager = EventManager()
    return ev_Manager

