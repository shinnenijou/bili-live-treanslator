from configparser import RawConfigParser
from threading import Thread
import gc
from multiprocessing import Queue as p_Queue

from config import CONFIG_ROOT, EConfigType, ConfigFile, EProcessStatus, EProcessCommand
from .recognizer import ASRRecognizer

CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Global])

# ASR recognizer
recognizer = None

# communication thread
t_communicate = None


def run(speech_queue, translate_queue, gui_text_queue, asr_queue):
    """
    ASR process entry
    :return: None
    """
    if not init(speech_queue, translate_queue, gui_text_queue, asr_queue):
        asr_queue.put(EProcessStatus.Error)
        return
    else:
        asr_queue.put(EProcessStatus.Init)

    t_communicate.start()

    # Block Here!
    recognizer.start()

    t_communicate.join()

    destroy()


def init(speech_queue, translate_queue, gui_text_queue, asr_queue):

    # Init recognizer
    global recognizer
    recognizer = ASRRecognizer(CONFIG['global']['ASR_MODEL'], speech_queue, translate_queue, gui_text_queue)

    # Init communication thread
    global t_communicate
    t_communicate = Thread(target=listen_command, args=(asr_queue, ))

    return True


def destroy():
    # Destroy communication thread
    global t_communicate
    t_communicate = None
    pass

    # Destroy recognizer
    global recognizer
    recognizer = None

    gc.collect()


def update_config():
    global CONFIG, recognizer
    CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Global])

    if recognizer is None:
        return

    recognizer.update_config(CONFIG['global']['ASR_MODEL'])


def listen_command(command_queue: p_Queue):
    while True:
        command = command_queue.get(block=True)
        if command == EProcessCommand.Stop:
            if recognizer is None:
                continue

            recognizer.stop()
            break
