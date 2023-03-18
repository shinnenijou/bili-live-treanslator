CONFIG_ROOT = 'config/'
MODEL_ROOT = 'res/model/'
TEMP_ROOT = '.temp/'


class EConfigType:
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


class EProcessStatus:
    Init = 0
    Running = 1
    Error = 2
    Stop = 3


class EProcessCommand:
    Start = 0
    Stop = 1
