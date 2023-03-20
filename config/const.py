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


GlobalTitleToOption = {
    'global': {
        '翻译接口': 'translator',
        '语音识别模型': 'asr_model',
    }
}


TranslateTitleToOption = {
    'baidu': {
        'API': 'api',
        'APPID': 'appid',
        'KEY': 'key',
        '源语言': 'from',
        '目标语言': 'to',
        '重试次数': 'retry_limit',
    }
}

BilibiliTitleToOption = {
    'room': {
        '直播间号': 'target_room',
        '发送间隔': 'send_interval',
    },
    'user': {
        'SESSDATA': 'sessdata',
        'BILI_JCT': 'bili_jct',
        'BUVID3': 'buvid3',
    }
}


class Const:
    AppTitle = '同传鸡'
    AppSize = '640x360'
    UpdateInterval = 100


class EProcessStatus:
    Ready = 0
    Running = 1
    Error = 2
    Stop = 3


class EProcessCommand:
    Start = 0
    Stop = 1
