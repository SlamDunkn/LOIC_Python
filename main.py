import sys, socket, string, random, os
from Events import *
from IRC import * 

def lazerHook(event):
    print event.arg

    targetip = None
    targethost = None
    timeout = None
    subsite = None
    message = None
    port = None
    method = None
    threads = None
    wait = None
    random = None
    speed = None

    s = event.arg
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


def main(args):
    print args

    listener = Listener(START_LAZER, lazerHook)
    getEventManager().addListener(listener)
    irc = IRC(args[1], int(args[2]), args[3])

    while 1:
        i = raw_input()
        if i == "quit" or i == "exit":
            irc.stop()
            break


if __name__ == '__main__':
    args = []
    for arg in sys.argv:
        args.append(arg)
    main(args)
