import requests
import json
from time import time as nowtime
from configparser import RawConfigParser
from .bilibili_enum import *

CONFIG = RawConfigParser()
CONFIG.read('config/bilibili_config.ini')
CONFIG = CONFIG['bilibili']


class DanmakuSender:
    """弹幕发送机"""
    def __init__(self, room_id: str, sessdata, bili_jct, buvid3, timeout=(3.05,5)):
        self.__room_id = room_id
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30',
            'Origin': f'https://live.bilibili.com',
            'Referer': f'https://live.bilibili.com/{room_id}'
        }
        self.__timeout = timeout
        self.__url = "https://api.live.bilibili.com/msg/send"
        self.__session = requests.session()
        cookie = f'buvid3={buvid3};SESSDATA={sessdata};bili_jct={bili_jct}'
        requests.utils.add_dict_to_cookiejar(self.__session.cookies, {"Cookie": cookie})
        self.__csrf = bili_jct

        # danmaku config
        self.__mode = EDanmakuPosition.Roll
        self.__color = EDanmakuColor.White

    def __post(self, url: str, data: dict) -> tuple[ESendResult, requests.Response|None]:
        result = ESendResult.Fail
        resp = None
        try:
            resp = self.__session.post(url=url, headers=self.__headers, data=data, timeout=self.__timeout)
            result = ESendResult.Success
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            pass

        return result, resp

    def __send(self, msg: str, mode: int, color: int) -> tuple[ESendResult, dict]:
        data={
            "color": color,
            "fontsize": 25,
            "mode": mode,
            "bubble": 0,
            "msg": msg,
            "roomid": self.__room_id,
            "rnd": nowtime(),
            "csrf_token": self.__csrf,
            "csrf": self.__csrf,
        }
        result, resp = self.__post(self.__url, data)
        if result != ESendResult.SendFail and resp.status_code == EHTTPStatusCode.OK:
            resp = json.loads(resp.text)
            result = resp['code']

        return result, resp

    def send(self, msg: str, mode=1):
        """
        向直播间发送弹幕
        :param msg:待发送
        :param mode:
        :param number:
        :param timeout:
        :return:
        """
        result, resp = self.__send(msg, self.__mode, self.__color)



        return resp