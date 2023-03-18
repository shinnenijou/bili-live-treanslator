from multiprocessing import Queue as p_Queue
from configparser import RawConfigParser, SectionProxy

import utils
from config import CONFIG_ROOT, ConfigFile, EConfigType
from . import baidu

translator = None


CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Translate])


def init(name: str, src_queue: p_Queue, send_queue: p_Queue):
    global translator

    translator_map = {
        'Baidu': baidu.Translator
    }

    if name not in translator_map:
        utils.logger.error(f"未知的翻译器: {name}, 请检查全局配置")
        return False

    if not CONFIG.has_section(name):
        utils.logger.error("缺少翻译器配置, 请检查翻译器设置")
        return False

    translator = translator_map[name](
        _src_queue=src_queue,
        _send_queue= send_queue,
        _name=name,
        _config=CONFIG[name]
    )

    if not translator.validate_config():
        utils.logger.error("[error]翻译器配置错误, 请检查翻译器设置")
        return False

    return True


def destroy():
    global translator
    translator = None


def update_config():
    global CONFIG, translator
    CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Translate])

    if translator is None:
        return

    translator.update_config(CONFIG[translator.get_name()])