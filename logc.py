import logging
import socketserver
import grokkk
from datetime import datetime
from elasticsearch import Elasticsearch
from multiprocessing import Process, Queue

LOG_FILE = "./logfiles/asa5550.log"
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


def logcollect(q, testDict):
    """
    docstring
    """

    class SyslogUDPHandler(socketserver.BaseRequestHandler):

        def handle(self):
            # data = bytes.decode(self.request[0].strip())
            data = bytes.decode(self.request[0].rstrip(b'\x00'))
            pa = testDict[self.client_address[0]]
            for keyworld, pattern in pa.items():
                if keyworld in str(data):
                    # use my gork
                    patterCompiled = grokkk.compile(pattern)
                    doc = grokkk.outputtt(patterCompiled, str(data))
                    doc["timestamp"] = datetime.now()
                    # print(doc)
                    # write to ES   write to queen
                    q.put(doc)
                    # after a function is executed the variables within the function are aotomactically deleted,except for closures
                    # del data
                    # del pa
                    # del patterCompiled
                    # del doc
                    # del keyworld
                    # del pattern
                    break

    try:
        HOST, PORT = "0.0.0.0", 2333
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise


def writeEs(q):
    """
    docstring
    """
    client = Elasticsearch(
        "https://192.168.1.42:9200",
        basic_auth=("elastic", "123456"),
        ssl_assert_fingerprint=
        "b6e3e9649408c78ee13d6472a041b4e068574bdeaaa43d6947a33b7f7349a07c")
    while True:
        if not q.empty():
            doc = q.get(True)
            # logging.info(str(doc))
            # print(doc)
            # TODO try capture error
            resp = client.index(index="logtest5", document=doc)


if __name__ == "__main__":
    print('start...')
    q = Queue()
    #父进程的queue传递给子进程
    pw = Process(target=logcollect, args=(
        q,
        testDict,
    ))
    pr = Process(target=writeEs, args=(q, ))

    pw.start()
    pr.start()
    pr.join()
    pw.join()

    # except KeyboardInterrupt:
    #     print("Crtl+C Pressed. Shutting down.")