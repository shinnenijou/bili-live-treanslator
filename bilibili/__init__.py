from configparser import RawConfigParser
from multiprocessing import Queue as p_Queue

from config import CONFIG_ROOT, EConfigType, ConfigFile
from .danmaku_sender import DanmakuSender
import utils

# Config
CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])

# Danmaku Sender
sender = None

# Danmaku Anti Shield
anti_shield = None


def init(send_queue, gui_text_queue):
    global sender, anti_shield
    send_queue = p_Queue(maxsize=0)

    sender = DanmakuSender(
        send_queue=send_queue,
        show_queue=gui_text_queue,
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3'],
        send_interval=CONFIG['room']['SEND_INTERVAL']
    )

    if sender.get_user_info() == '':
        utils.logger.error("获取用户信息, 请检查配置文件")
        return False

    if sender.get_danmaku_config() == (None, None):
        utils.logger.error("获取弹幕配置失败, 请检查配置文件")
        return False

    return True


def destroy():
    global sender, anti_shield
    sender = None
    anti_shield = None


def update_config():
    global CONFIG, sender
    CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])

    if sender is None:
        return

    sender.update_config(
        room_id=CONFIG['room']['TARGET_ROOM'],
        sessdata=CONFIG['user']['SESSDATA'],
        bili_jct=CONFIG['user']['BILI_JCT'],
        buvid3=CONFIG['user']['BUVID3']
    )
