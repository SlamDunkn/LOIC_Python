import socket, threading, random, time
from Events import *

def randomString(length):
    allowedChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    string = ''.join(random.choice(allowedChars) for i in xrange(length))
    return string

class ListenThread(threading.Thread):

    def __init__(self, socket, irc):
        threading.Thread.__init__(self)

        self.socket = socket
        self.irc = irc
        self.readBuffer = ""
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                self.readBuffer += self.socket.recv(1024)
            except:
                pass

            while self.readBuffer.find('\n') >= 0:
                breakPoint = self.readBuffer.find('\n')
                line = self.readBuffer[0:breakPoint].replace('\r', '')
                self.readBuffer = self.readBuffer[breakPoint+1:]
                event = Event(IRC_RECV, line)
                getEventManager().signalEvent(event)
        

class IRC:

    def __init__(self, host, port, channel):
        self.host = host
        self.port = port
        self.channel = channel
        self.socket = socket.socket()
        self.socket.settimeout(5)

        self.nick = "LOIC_" + randomString(5)
        self.ops = []

        listener = Listener(IRC_RECV, self.parseIRCString)
        getEventManager().addListener(listener)

        self.connect()

    def connect(self):
        self.listenThread = ListenThread(self.socket, self)

        try:
            self.socket.connect((self.host, self.port))
        except:
            print "Random error connecting, aborting"
            return

        self.listenThread.start()

        self.socket.send("NICK %s\r\n" % self.nick)
        self.socket.send("USER IRCLOIC %s blah :SlamDunk's Remote Python LOIC\r\n" % self.host)

    def deleteOp(self, op):
        self.ops[:] = (value for value in self.ops if value != op)

    def parseIRCString(self, event):
        string = event.arg
        if string.find("PING") == 0:
            self.socket.send("PONG " + string[5:] + "\r\n")
            print "PONG", string[5:]
        elif string[0] == ":":
            print string
            info = string.split(" ")
            if info[1] == "PRIVMSG" and info[2] == self.channel:
                if len(info) > 4 and info[3].lower() == ":!lazer":
                    name = info[0][1:info[0].find('!')]
                    if name in self.ops:
                        event = Event(LAZER_RECV, info[4:])
                        getEventManager().signalEvent(event)
            elif info[1] == "MODE" and info[2] == self.channel:
                if info[3] == "+o":
                    self.ops.append(info[4])
                elif info[3] == "-o":
                    self.deleteOp(info[4])
            elif info[2] == self.nick and info[3] == "=" and info[4] == self.channel:
                for op in info[5:]:
                    op = op.replace(':', '')
                    if op[0] == "@":
                        self.ops.append(op[1:])
                print "Connection succesful, waiting for lazer charge"
            elif info[1] == "002":
                self.socket.send("JOIN %s\r\n" % self.channel)
                print "Joining", self.channel
        else:
            print "SCRAP", string
            if string == "ERROR :All connections in use":
                print "retrying in 5 seconds"
                self.stop()
                self.socket = socket.socket()

                event = Event(IRC_RESTART, None)
                getEventManager().signalEvent(event)

    def stop(self):
        self.listenThread.stop()
        
