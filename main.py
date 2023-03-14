import translate
import bilibili

from multiprocessing import Process, Queue
from configparser import ConfigParser
from threading import Thread

CONFIG = ConfigParser()
CONFIG.read('config/config.ini')

if __name__ == '__main__':
    src_text_queue = Queue(maxsize=0)
    send_queue = Queue(maxsize=0)

    p_translator = Thread(
        target=translate.run,
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
        text = input("Text to translate: ")
        src_text_queue.put(text, block=True)

        if text == 'exit':
            break

    p_translator.join()
    p_sender.join()

    exit(0)