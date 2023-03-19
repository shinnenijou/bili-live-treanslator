from multiprocessing import Queue as p_Queue

from config import config
from .danmaku_sender import DanmakuSender
import utils

# Danmaku Sender
sender = None

# Danmaku Anti Shield
anti_shield = None


def init(send_queue: p_Queue, gui_text_queue: p_Queue):
    global sender, anti_shield

    sender = DanmakuSender(
        send_queue=send_queue,
        show_queue=gui_text_queue,
        room_id=config.bilibili['room']['target_room'],
        sessdata=config.bilibili['user']['sessdata'],
        bili_jct=config.bilibili['user']['bili_jct'],
        buvid3=config.bilibili['user']['buvid3'],
        send_interval=float(config.bilibili['room']['send_interval'])
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
    global sender

    if sender is None:
        return

    sender.update_config(
        room_id=config.bilibili['room']['target_room'],
        sessdata=config.bilibili['user']['sessdata'],
        bili_jct=config.bilibili['user']['bili_jct'],
        buvid3=config.bilibili['user']['buvid3'],
    )
