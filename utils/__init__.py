import os
import shutil
from multiprocessing import Queue as p_Queue
from time import strftime, localtime

import ffmpeg

logger = None


class Logger():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, gui_text_queue: p_Queue):
        self.__gui_text_queue = gui_text_queue

    def info(self, text: str):
        self.__gui_text_queue.put(f'[info]{text}')

    def warn(self, text: str):
        self.__gui_text_queue.put(f'[warn]{text}')

    def error(self, text: str):
        self.__gui_text_queue.put(f'[error]{text}')


def init(gui_text_queue: p_Queue):
    global logger
    logger = Logger(gui_text_queue)


def mkdir(path: str):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    except Exception as e:
        print(e)


def remove(path: str):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)


def rm(file: str):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)


def touch(file: str):
    try:
        open(file, 'x')
    except FileExistsError:
        pass
    except Exception as e:
        print(e)


def get_all(queue: p_Queue) -> list[str]:
    """
    弹出当前同步队列里的所有元素, 队列里没有元素时将会被阻塞, 一旦有元素后将全部取走
    :param queue:待弹出元素的队列
    :return:返回一个弹出元素的有序列表, 顺序同出队顺序
    """
    ret = []
    element = queue.get(block=True)
    ret.append(element)
    while not queue.empty():
        element = queue.get_nowait()
        ret.append(element)

    return ret


def clear(queue: p_Queue):
    """
    清空同步队列里的所有元素
    :param queue:待清空的队列
    """
    while not queue.empty():
        queue.get_nowait()


def hms_time() -> str:
    """
    获取当前hh:mm:ss时间
    :return:当前hh:mm:ss时间字符串
    """
    return strftime('%H:%M:%S', localtime())


def transcode_to_audio(file_path):
    new_file = file_path.rsplit('.', 1)[0] + '.mp3'
    try:
        ffmpeg.input(file_path).output(new_file).run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print(f"Failed to load audio: {e.stderr.decode()}")

    return new_file


def isfile(path: str):
    return os.path.isfile(path)


def isdir(path: str):
    return os.path.isdir(path)


def debug(msg: str):
    if os.getenv('DEBUG') == '1':
        print(msg)

class AntiRecognizer:
    def __init__(self):
        try:
            with open('config/anti_recognize.txt', 'r', encoding='utf-8') as f:
                anti_recognize = f.read().splitlines()
        except FileNotFoundError:
            anti_recognize = []

        self.__anti_recognize = anti_recognize

    def preprocess(self, text: str):
        for word in self.__anti_recognize:
            text = text.replace(word, '')

        return text

anti_recognize = AntiRecognizer()