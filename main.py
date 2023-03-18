from multiprocessing import Process, Queue as p_Queue
from configparser import ConfigParser
from threading import Thread
import gc

import translator
import bilibili
import framework
import utils

CONFIG = ConfigParser()
CONFIG.read('config/config.ini')

# Sync Queue
gui_text_queue = p_Queue(maxsize=0)
danmaku_send_queue = None
speech_text_queue = None

# Process

# Thread
t_sender = None
t_translator = None


def start_process():
    # Make temp directory
    utils.mkdir('.temp')

    # Init Sync Queue
    global danmaku_send_queue, speech_text_queue
    danmaku_send_queue = p_Queue(maxsize=0)
    speech_text_queue = p_Queue(maxsize=0)

    # Init Threads
    global t_translator, t_sender

    if not translator.init(CONFIG['global']['TRANSLATOR'], speech_text_queue, danmaku_send_queue):
        destroy_process()
        return False
    utils.logger.info('翻译组件初始化完成...')
    t_translator = Thread(target=translator.translator.start)

    if not bilibili.init(danmaku_send_queue, gui_text_queue):
        destroy_process()
        return False
    utils.logger.info(f'发送组件初始化完成, 用户: {bilibili.sender.get_name()}')
    t_sender = Thread(target=bilibili.sender.start)

    # Start Threads
    utils.logger.info('初始化完成, 翻译机开始运行')
    t_translator.start()
    t_sender.start()

    return True


def destroy_process():
    # Remove temp directory
    utils.remove('.temp')

    # Destroy Sync Queue
    global danmaku_send_queue, speech_text_queue
    danmaku_send_queue = None
    speech_text_queue = None

    # Destroy Threads
    global t_sender, t_translator

    bilibili.destroy()
    t_sender = None

    translator.destroy()
    t_translator = None

    gc.collect()


def stop_process():
    # Stop Threads
    if t_translator is not None:
        translator.translator.stop()
        t_translator.join()
        utils.logger.info('成功停止翻译组件...')

    if t_sender is not None:
        bilibili.sender.stop()
        t_sender.join()
        utils.logger.info('成功停止发送组件...')

    # Remove temp directory
    utils.remove('.temp')

    utils.logger.info('翻译机已停止运行')

    return True


if __name__ == '__main__':
    framework.init()
    utils.init(gui_text_queue)

    framework.run(gui_text_queue, start_process, stop_process)