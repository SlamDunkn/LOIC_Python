import socket, threading, random
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
            self.readBuffer += self.socket.recv(1024)

            while self.readBuffer.find('\n') >= 0:
                breakPoint = self.readBuffer.find('\n')
                line = self.readBuffer[0:breakPoint]
                self.readBuffer = self.readBuffer[breakPoint+1:]
                self.irc.parseIRCString(line)
        

class IRC:

    def __init__(self, host, port, channel):
        self.host = host
        self.port = port
        self.channel = channel
        self.socket = socket.socket()
        self.listenThread = ListenThread(self.socket, self)

        self.nick = "LOIC_" + randomString(5)

        self.socket.connect((self.host, self.port))
        self.socket.send("NICK %s\r\n" % self.nick)
        self.socket.send("USER IRCLOIC-Python %s blah :SlamDunk's Remote Python LOIC\r\n" % self.host)

        self.socket.send("JOIN %s\r\n" % self.channel)

        self.listenThread.start()

    def parseIRCString(self, string):
        if string[0] == "PING":
            self.socket.send("PONG" + string[5:])
            print "PONG", string[5:]
        elif string[0] == ":":
            print string
        elif string[0] == "PRIVMSG":
            info = string[8:].split(" ")
            print info
        else:
            print "SCRAP", string

            #event = Event(IRC_RECV, line)
            #getEventManager().addEvent(event)

    def stop(self):
        self.listenThread.stop()
        
