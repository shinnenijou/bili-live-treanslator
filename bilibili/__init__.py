from bilibili_api import Credential, live, Danmaku, sync
from configparser import RawConfigParser
from multiprocessing import Queue
from time import sleep

CONFIG = RawConfigParser()
CONFIG.read('config/bilibili_config.ini')
CONFIG = CONFIG['bilibili']

CREDENTIAL = Credential(sessdata=CONFIG['SESSDATA'], bili_jct=CONFIG['BILIJCT'], buvid3=CONFIG['BUVID3'])


def send_danmaku(room, text):
    try:
        sync(room.send_danmaku(Danmaku(text=text)))
    except Exception as e:
        print(str(e))
        pass


def run(send_queue: Queue):
    room = live.LiveRoom(CONFIG['TARGET_ROOM'], CREDENTIAL)
    sleep_interval = int(CONFIG['SEND_INTERVAL'])

    while True:
        text = send_queue.get(block=True)
        if text == 'exit':
            break

        send_danmaku(room, text)
        sleep(sleep_interval)

    exit(0)