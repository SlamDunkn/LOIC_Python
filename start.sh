#!/bin/bash
if [ ! -f Core/synmod.so ]; then
    cd SYNModule
    ./build.sh
    mv synmod.so ../Core/
fi

#python main.py irc.hiddenaces.net 6667 \#loic
