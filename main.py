import translator
import bilibili
import framework

from multiprocessing import Process, Queue as p_Queue
from configparser import ConfigParser
from threading import Thread

CONFIG = ConfigParser()
CONFIG.read('config/config.ini')

def main():
    src_text_queue = p_Queue(maxsize=0)
    send_queue = p_Queue(maxsize=0)

    p_translator = Thread(
        target=translator.run,
        name='translator',
        args=(
            CONFIG['GLOBAL']['TRANSLATOR'],
            src_text_queue,
            send_queue,
        )
    )

    p_translator.start()

    p_sender = Thread(
        target=bilibili.run,
        name='danmaku_sender',
        args=(
            send_queue,
        )
    )

    p_sender.start()

    while True:
        text = input("Text to translator: ")
        src_text_queue.put(text, block=True)

        if text == 'exit':
            break

    p_translator.join()
    p_sender.join()

    exit(0)


if __name__ == '__main__':
    gui_text_queue = p_Queue(maxsize=0)
    framework.run(gui_text_queue)