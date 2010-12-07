import mutex

IRC_RECV = 1

class Event:

    def __init__(self, typeID, arg = None):
        self.typeID = typeID
        self.arg = arg

class Listener:

    def __init__(self, typeID, function):
        self.typeID == typeID
        self.function = function
        

class EventManager:

    def __init__(self):
        self.__eventStack = []
        self.__listeners = []
        self.__mutex = mutex.mutex()

    def signalEvent(self, event):
        self.__mutex.lock()
        for l in self.__listeners:
            if l.typeID == event.typeID:
                l.function(event)
        self.__mutex.unlock()

    def addListener(self, listener):
        self.__listeners.append(listener)

ev_Manager = None

def getEventManager():
    if ev_Manager == None:
        ev_Manager = EventManager()
    return ev_Manager

