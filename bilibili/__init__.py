from configparser import RawConfigParser
from multiprocessing import Queue as p_Queue

from config import CONFIG_ROOT, EConfigType, ConfigFile
from .danmaku_sender import DanmakuSender

# Config
CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])

# Danmaku Sender
SENDER = DanmakuSender(
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3']
    )

# Danmaku Anti Shield
ANTI_SHIELD = None


def update_config():
    global CONFIG

    CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])
    SENDER.update_config(
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3']
    )

