#This requires cygwin.
gcc -shared -I /C/Python26/include -L /C/Python26/libs windows-module.c -lpython26 -lws2_32 -export-all-symbols -o synmod.pyd
