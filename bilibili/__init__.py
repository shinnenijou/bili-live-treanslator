from configparser import RawConfigParser
from . import danmaku_sender
from multiprocessing import Queue
from time import sleep

CONFIG = RawConfigParser()
CONFIG.read('config/bilibili_config.ini')
CONFIG = CONFIG['bilibili']

def run(send_queue: Queue):
    sender = danmaku_sender.DanmakuSender(CONFIG['TARGET_ROOM'], sessdata=CONFIG['SESSDATA'], bili_jct=CONFIG['BILI_JCT'], buvid3=CONFIG['BUVID3'])

    while True:
        text = send_queue.get(block=True)
        if text == 'exit':
            break

        resp = sender.send(text)
        print(resp)

    exit(0)
