import logging
import socketserver
from grokkk import compile, outputtt
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
testDict = {"172.21.224.1": {"sss": PATTERN, "uuu": PATTERN, "fff": PATTERN}}


def logcollect(qdata):
    """
    docstring
    """

    class SyslogUDPHandler(socketserver.BaseRequestHandler):

        def handle(self):
            # data = bytes.decode(self.request[0].strip())
            # format ['str',ip]
            data = [
                bytes.decode(self.request[0].rstrip(b'\x00')),
                self.client_address[0]
            ]

            # print(data)
            # write to data queue
            qdata.put(data)
            # after a function is executed the variables within the function are aotomactically deleted,except for closures
            # del data

    try:
        HOST, PORT = "0.0.0.0", 2333
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise


def dataParse(qdata, qdataParsed, testDict):
    """
    docstring
    """
    while True:
        if not qdata.empty():
            data = qdata.get(True)
            # NOTE 资产没找到解析模板，返回一个默认值 {}
            pa = testDict.get(data[1], {})
            pattern = "nopattern"
            # TODO try
            for keyworld, pat in pa.items():
                if keyworld in data[0]:
                    pattern = pat
                    break
            if pattern == "nopattern":
                dataParsed = {'raw': data[0], 'timestamp': datetime.now()}
                qdataParsed.put(
                    dataParsed)  # write raw data to qdataParsed queue
            else:
                # use my gork
                # TODO try
                patternCompiled = compile(pattern)
                dataParsed = outputtt(patternCompiled, data[0])
                dataParsed["timestamp"] = datetime.now()
                dataParsed["raw"] = data[0]
                qdataParsed.put(dataParsed)


def writeEs(qdataParsed):
    """
    docstring
    """
    client = Elasticsearch(
        "https://192.168.1.42:9200",
        basic_auth=("elastic", "123456"),
        ssl_assert_fingerprint=
        "b6e3e9649408c78ee13d6472a041b4e068574bdeaaa43d6947a33b7f7349a07c")

    while True:
        if not qdataParsed.empty():
            dataParsed = qdataParsed.get(True)
            logging.info(str(dataParsed))
            print(dataParsed)
            # TODO try capture error
            # TODO es bulk insert
            # resp = client.index(index="logtest6", document=dataParsed)


if __name__ == "__main__":
    print('start...')
    qdata = Queue()
    qdataParsed = Queue()
    #父进程的queue传递给子进程
    plogc = Process(target=logcollect, args=(qdata, ))
    pparse = Process(target=dataParse, args=(
        qdata,
        qdataParsed,
        testDict,
    ))
    pwriteEs = Process(target=writeEs, args=(qdataParsed, ))

    plogc.start()
    pparse.start()
    pwriteEs.start()
    plogc.join()
    pparse.join()
    pwriteEs.join()

    # except KeyboardInterrupt:
    #     print("Crtl+C Pressed. Shutting down.")