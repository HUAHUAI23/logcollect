import logging
import socketserver
import grokkk
from pygrok import Grok
from datetime import datetime
from pprint import pprint
from elasticsearch import Elasticsearch

client = Elasticsearch(
    "https://192.168.1.42:9200",
    basic_auth=("elastic", "123456"),
    ssl_assert_fingerprint=
    "b6e3e9649408c78ee13d6472a041b4e068574bdeaaa43d6947a33b7f7349a07c")

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
testDict = {"172.18.160.1": {"sss": PATTERN, "uuu": PATTERN, "fff": PATTERN}}


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
                # use Pygrok
                # grok = Grok(pattern, custom_patterns={"TEMP": ".*"})
                # logging.info(grok.match(str(data)))
                # print(grok.match(str(data)))
                # del grok
                # use my gork
                patterCompiled = grokkk.compile(pattern)
                # write to log file
                logging.info(grokkk.outputtt(patterCompiled, str(data)))
                # print(grokkk.outputtt(patterCompiled, str(data)))
                doc = grokkk.outputtt(patterCompiled, str(data))
                doc["timestamp"] = datetime.now()
                print(doc)
                # write to ES
                resp = client.index(index="logtest2", document=doc)
                # print(resp.body)
                del patterCompiled
                del doc
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
