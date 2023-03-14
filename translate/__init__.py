from . import baidu_api
from multiprocessing import Queue
from loguru import logger

Translator = {
    'Baidu': baidu_api.Translator
}


def get_all(queue: Queue) -> list[str]:
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


def run(translator_name: str, src_queue: Queue, send_queue: Queue):
    if translator_name not in Translator:
        logger.error(f"Translator not exists: {translator_name}")
        exit(0)

    translator = Translator[translator_name]('jp', 'zh')
    while True:
        src_text = get_all(src_queue)
        if src_text[0] == 'exit':
            send_queue.put(src_text[0], block=True)
            break

        dst_text = translator.translate(*src_text)
        for text in dst_text:
            send_queue.put(text, block=True)

    exit(0)


if __name__ == '__main__':
    print("hello, I'm translator")