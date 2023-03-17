from enum import Enum

CONFIG_ROOT = 'config/'


class EConfigType(Enum):
    Global = 0
    Translate = 1
    Bilibili = 2


ConfigFile = {
    EConfigType.Global: 'config.ini',
    EConfigType.Translate: 'translate_config.ini',
    EConfigType.Bilibili: 'bilibili_config.ini'
}


GlobalDefault = {
    'GLOBAL': {
        'TRANSLATOR': 'Baidu'
    }
}


TranslateDefault = {
    'Baidu': {
        'API': '',
        'APPID': '',
        'KEY': '',
        'RETRY': 0,
        'ASYNC': False
    }
}

class Const:
    AppTitle = '同传鸡'
    AppSize = '480x270'
    UpdateInterval = 100
