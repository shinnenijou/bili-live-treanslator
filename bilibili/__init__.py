from configparser import RawConfigParser
from queue import Queue as t_Queue
from config import CONFIG_ROOT, EConfigType, ConfigFile
from .danmaku_sender import DanmakuSender

# Config
CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])

# Danmaku Sender
sender = None

# Danmaku Anti Shield
ANTI_SHIELD = None


def init(send_queue: t_Queue, show_queue: t_Queue):
    global sender
    sender = DanmakuSender(
        send_queue=send_queue,
        show_queue=show_queue,
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3']
    )

    if sender.get_user_info() == '':
        show_queue.put(">>> 获取用户信息, 请检查配置文件")
        return False

    if sender.get_danmaku_config() == (None, None):
        show_queue.put(">>> 获取弹幕配置失败, 请检查配置文件")
        return False

    return True


def update_config():
    global CONFIG
    CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])

    if sender is None:
        return

    sender.update_config(
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3']
    )
