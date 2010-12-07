import sys, socket, string, random, os
from Events import *
from IRC import * 

def main(args):
    print args

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
