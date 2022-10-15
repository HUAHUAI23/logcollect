import logging
import logging.handlers  # handlers要单独import

logger = logging.getLogger()
fh = logging.handlers.SysLogHandler(
    ('127.0.0.1', 1514), logging.handlers.SysLogHandler.LOG_AUTH)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(20)
# logger.warning("sss")
logger.warning("sss")
# logger.error('''alert[9148]: {"node_area":"Hit\u5b89\u5168\u533a","first_timestamp":"2022-01-21T15:06:38","last_timestamp":"2022-01-21T15:06:38","flow_id":1081759915496766,"node_ip":"192.168.45.11","node_id":"6C92BF0B87B9","event_hash":"150d8e0dab50d87dc62f6c836d5fb0b0","event_id":"1081759915496766","proto":"ICMP","app_proto":"","source":"honeypot","in_iface":"enp132s0f0","network":{"src":{"ip":"10.160.12.229","mac":"c0:bf:a7:ec:8e:e1","port":0},"dst":{"ip":"10.160.12.4","port":0,"mac":"a0:36:9f:51:46:ee"},"attacker_info":{"city":"","country":"\u5c40\u57df\u7f51","iso_code":"","latitude":0.0,"longitude":0.0,"province":"","time_zone":"","continent":"","ip":"10.160.12.229"}''')