from . import baidu_api
from multiprocessing import Queue
import utils

Translator = {
    'Baidu': baidu_api.Translator
}


def run(translator_name: str, src_queue: Queue, send_queue: Queue):
    if translator_name not in Translator:
        #logger.error(f"Translator not exists: {translator_name}")
        exit(0)

    translator = Translator[translator_name]('jp', 'zh')
    while True:
        src_text = utils.get_all(src_queue)
        if src_text[0] == 'exit':
            send_queue.put(src_text[0], block=True)
            break

        dst_text = translator.translate(*src_text)
        for text in dst_text:
            send_queue.put(text, block=True)

    exit(0)


if __name__ == '__main__':
    print("hello, I'm translator")