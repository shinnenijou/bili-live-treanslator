import os
import shutil
from multiprocessing import Queue as p_Queue
from queue import Queue as t_Queue, Empty


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


def get_all(queue: [p_Queue, t_Queue]) -> list[str]:
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
