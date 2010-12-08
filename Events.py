IRC_RECV = 1
START_LAZER = 2

class Event:

    def __init__(self, typeID, arg = None):
        self.typeID = typeID
        self.arg = arg

class Listener:

    def __init__(self, typeID, function):
        self.typeID = typeID
        self.function = function
        

class EventManager:

    def __init__(self):
        self.__eventStack = []
        self.__listeners = []

    def signalEvent(self, event):
        print "got Event"
        for l in self.__listeners:
            if l.typeID == event.typeID:
                l.function(event)

    def addListener(self, listener):
        self.__listeners.append(listener)

ev_Manager = None

def getEventManager():
    global ev_Manager
    if ev_Manager == None:
        ev_Manager = EventManager()
    return ev_Manager

