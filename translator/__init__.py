from multiprocessing import Queue as p_Queue

import utils
from config import config
from . import baidu

translator = None


def init(name: str, translate_queue: p_Queue, send_queue: p_Queue):
    global translator

    translator_map = {
        'Baidu': baidu.Translator
    }

    if name not in translator_map:
        utils.logger.error(f"未知的翻译器: {name}, 请检查全局配置")
        return False

    translator = translator_map[name](
        _src_queue=translate_queue,
        _send_queue=send_queue,
        _name=name,
        _config=config.translate[name]
    )

    if not translator.validate_config():
        utils.logger.error("[error]翻译器配置错误, 请检查翻译器设置")
        return False

    return True


def destroy():
    global translator
    translator = None


def update_config():
    global translator

    if translator is None:
        return

    translator.update_config(config.translate[translator.get_name()])