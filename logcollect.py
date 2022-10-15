import logging
import socketserver
from urllib import request
import grokkk
from pygrok import Grok

LOG_FILE = "./asa5550.log"
a = 0
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="",
    filename=LOG_FILE,
    filemode="a",
)
# PATTERN = "%{TEMP:temp} - root - %{WORD:level} - %{WORD:message}"
PATTERN = "%{TEMP:temp} - root - %{WORD:level} - %{TEMP:temp}"
testDict = {"172.21.80.1": {"sss": PATTERN, "uuu": PATTERN}}


class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # data = bytes.decode(self.request[0].strip())
        data = bytes.decode(self.request[0].rstrip(b'\x00'))
        # socket = self.request[1]
        # print("%s : " % self.client_address[0], str(data))
        # print(self.client_address[0])
        # print(str(data))
        # logging.info(str(data))
        pa = testDict[self.client_address[0]]
        for keyworld, pattern in pa.items():
            if keyworld in str(data):
                # grok = Grok(pattern, custom_patterns={"TEMP": ".*"})
                # logging.info(grok.match(str(data)))
                # print(grok.match(str(data)))
                # del grok

                patterCompiled = grokkk.compile(pattern)
                logging.info(grokkk.outputtt(patterCompiled, str(data)))
                print(grokkk.outputtt(patterCompiled, str(data)))
                del patterCompiled
                break

        global a
        a = a + 1
        # logging.info(grok.match(str(data)))
        print(a)


#        socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    try:
        HOST, PORT = "0.0.0.0", 1514
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")
