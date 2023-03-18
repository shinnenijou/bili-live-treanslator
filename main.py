from multiprocessing import Process, Queue as p_Queue
from configparser import ConfigParser
from threading import Thread
import gc
import os

import translator
import bilibili
import framework
import utils
import asr
from config import CONFIG_ROOT, EConfigType, ConfigFile, EProcessStatus, EProcessCommand

# Global Config
CONFIG = ConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Global])

# Sync Queue
gui_text_queue = None
asr_queue = None
speech_queue = None
translate_queue = None
danmaku_send_queue = None

# Process
p_recognizer = None

# Thread
t_sender = None
t_translator = None


def init_processes():
    """
    初始化进程, 包括主进程和子进程.
    :return: None
    """
    # Make temp directory
    utils.mkdir('.temp')

    # Global GUI text queue
    global gui_text_queue
    gui_text_queue = p_Queue(maxsize=0)

    # Global speech queue(wait to be recognized)
    global speech_queue
    speech_queue = p_Queue(maxsize=0)

    # Global translate queue(wait to be translated)
    global translate_queue
    translate_queue = p_Queue(maxsize=0)

    # Global danmaku send queue(wait to be sent)
    global danmaku_send_queue
    danmaku_send_queue = p_Queue(maxsize=0)

    # Queue for Communication with ASR process
    global asr_queue
    asr_queue = p_Queue(maxsize=0)

    # Init logger
    utils.init(gui_text_queue)

    if os.getenv('DEBUG') is not None and os.name == "posix":
        return True

    # Init ASR process(init in child process)
    global p_recognizer
    p_recognizer = Process(target=asr.run, args=(speech_queue, translate_queue, gui_text_queue, asr_queue, ))
    p_recognizer.start()
    result = asr_queue.get(block=True)
    if result != EProcessStatus.Init:
        destroy_processes()
        return False
    utils.logger.info('语音识别组件初始化完成...')

    return True


def start_processes():
    pass


def stop_processes():
    pass


def destroy_processes():
    """
    销毁进程, 包括主进程和子进程. 同时销毁主进程管理的所有线程.
    :return: None
    """
    # Notice ASR process to stop(destroy in child process)
    global p_recognizer, asr_queue
    if p_recognizer is not None:
        asr_queue.put(EProcessCommand.Stop)
        p_recognizer.join()
        p_recognizer = None

    # Destroy Threads
    destroy_threads()

    # Destroy Sync Queue
    global gui_text_queue, speech_queue, translate_queue, danmaku_send_queue
    gui_text_queue = None
    speech_queue = None
    translate_queue = None
    danmaku_send_queue = None
    asr_queue = None

    # Remove temp directory
    utils.remove('.temp')

    gc.collect()


def start_threads():
    # Init translator thread
    global t_translator
    if not translator.init(CONFIG['global']['TRANSLATOR'], translate_queue, danmaku_send_queue):
        destroy_threads()
        return False
    utils.logger.info('翻译组件初始化完成...')
    t_translator = Thread(target=translator.translator.start)

    # Init danmaku sender thread
    global t_sender
    if not bilibili.init(danmaku_send_queue, gui_text_queue):
        destroy_threads()
        return False
    utils.logger.info(f'发送组件初始化完成, 用户: {bilibili.sender.get_name()}')
    t_sender = Thread(target=bilibili.sender.start)

    # Start Threads
    utils.logger.info('初始化完成, 翻译机开始运行')
    t_translator.start()
    t_sender.start()

    return True


def stop_threads():

    global t_translator
    if t_translator is not None:
        translator.translator.stop()
        t_translator.join()
        utils.logger.info('成功停止翻译组件...')

    global t_sender
    if t_sender is not None:
        bilibili.sender.stop()
        t_sender.join()
        utils.logger.info('成功停止发送组件...')

    destroy_threads()
    utils.logger.info('翻译机已停止运行')

    return True


def destroy_threads():
    # Destroy Translator thread
    translator.destroy()
    global t_translator
    t_translator = None

    # Destroy Danmaku sender thread
    bilibili.destroy()
    global t_sender
    t_sender = None

    gc.collect()


if __name__ == '__main__':
    init_processes()

    framework.init()

    framework.run(gui_text_queue, start_threads, stop_threads, destroy_processes)