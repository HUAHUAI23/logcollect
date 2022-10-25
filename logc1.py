import logging
import socketserver
from gork import Grok
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
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
testDict = {
    "172.25.64.1": [
        "%{SYSLOG5424LINE}",
        '%{SYSLOG5424PRI}%{MYDATE:mydate} - %{HOSTNAME:syslog5424_host} - %{LOGLEVEL:loglevel} - %{GREEDYDATA:syslog5424_msg}'
    ],
    "127.0.0.1": ["%{SYSLOG5424LINE}"]
}


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
            # print(self.client_address[0])
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
    assetgrok = {}
    for asset, pats in testDict.items():
        assetgrok[asset] = Grok(
            pats[0],
            custom_patterns={
                'ID': '%{WORD}-%{INT}',
                'DATE_CN': '%{YEAR}[/-]%{MONTHNUM}[/-]%{MONTHDAY}',
                'MYDATE': "%{DATE_CN} %{TIME}"
            },
            custom_patterns_dir='/home/i42/pro/python/pygrok/pygrok/patterns')
        for pat in pats:
            assetgrok[asset].add_search_pattern(pat)
    while True:
        if not qdata.empty():
            data = qdata.get(True)
            # NOTE 没有找到资产的grok 返回None
            grok = assetgrok.get(data[1], None)
            if grok == None:
                dataParsed = {
                    'pckSrcIp': data[1],
                    'raw': data[0],
                    'timestamp': datetime.now()
                }
                qdataParsed.put(
                    dataParsed)  # write raw data to qdataParsed queue
            else:
                dataParsed = grok.match(data[0])
                if dataParsed == None:
                    dataParsed = {}
                dataParsed["timestamp"] = datetime.now()
                dataParsed["raw"] = data[0]
                dataParsed['pckSrcIp'] = data[1]
                qdataParsed.put(dataParsed)


def writeEs(qdataParsed):
    """
    docstring
    """
    esclient = Elasticsearch(
        "https://192.168.1.42:9200",
        basic_auth=("elastic", "123456"),
        ssl_assert_fingerprint=
        "b6e3e9649408c78ee13d6472a041b4e068574bdeaaa43d6947a33b7f7349a07c")

    # 生成器函数
    def es_generator():
        # NOTE 未设置迭代结束条件，将会是无穷迭代
        while True:
            if not qdataParsed.empty():
                dataParsed = qdataParsed.get(True)
                # print(dataParsed)
                # logging.info(str(dataParsed))
                yield {"_index": "logtest1", "_source": dataParsed}

    # NOTE 默认bulk为500，可通过参数 chunk_size 修改，具体参考:
    # https://elasticsearch-py.readthedocs.io/en/v8.4.3/helpers.html
    # https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/client-helpers.html
    # TODO try capture error
    helpers.bulk(esclient, actions=es_generator())


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