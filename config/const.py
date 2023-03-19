CONFIG_ROOT = 'config/'
MODEL_ROOT = 'res/model/'
TEMP_ROOT = '.temp/'


class EConfigType:
    Global = 0
    Translate = 1
    Bilibili = 2


ConfigFile = {
    EConfigType.Global: '.config.ini',
    EConfigType.Translate: '.translate_config.ini',
    EConfigType.Bilibili: '.bilibili_config.ini'
}


GlobalDefault = {
    'global': {
        'TRANSLATOR': 'Baidu',
    }
}


TranslateDefault = {
    'Baidu': {
        'API': 'https://fanyi-api.baidu.com/api/trans/vip/translate',
        'APPID': '',
        'KEY': '',
        'FROM': 'auto',
        'TO': 'zh',
        'RETRY_LIMIT': '2',
    }
}

BilibiliDefault = {
    'room': {
        'TARGET_ROOM': '',
        'SEND_INTERVAL': '0.5',
    },
    'user': {
        'SESSDATA': '',
        'BILI_JCT': '',
        'BUVID3': '',
    }
}


class Const:
    AppTitle = '同传鸡'
    AppSize = '640x360'
    UpdateInterval = 100


class EProcessStatus:
    Init = 0
    Running = 1
    Error = 2
    Stop = 3


class EProcessCommand:
    Start = 0
    Stop = 1
