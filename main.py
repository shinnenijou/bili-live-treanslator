import translator
import bilibili
import framework

from multiprocessing import Process, Queue as p_Queue
from configparser import ConfigParser
from threading import Thread
from queue import Queue as t_Queue

CONFIG = ConfigParser()
CONFIG.read('config/config.ini')


if __name__ == '__main__':
    gui_text_queue = t_Queue(maxsize=0)
    danmaku_send_queue = t_Queue(maxsize=0)
    #framework.run(gui_text_queue)
    if not bilibili.init(danmaku_send_queue, gui_text_queue):
        exit(1)

    t_sender = Thread(
        target=bilibili.sender.run
    )
    t_sender.start()

    while True:
        a = input('>>>')
        if a != '':
            bilibili.sender.stop()
            break

    t_sender.join()