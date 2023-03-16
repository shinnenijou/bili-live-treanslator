import configparser
import requests
import random
import hashlib
import asyncio
import json

CONFIG = configparser.ConfigParser()
CONFIG.read("config/translate_config.ini")
CONFIG = CONFIG['Baidu']


class Translator:
    def __init__(self, fr: str = 'jp', to: str = 'zh', api: str = CONFIG['API'], appid: str = CONFIG['APPID'],
                 key: str = CONFIG['KEY']):
        self.__api = api
        self.__appid = appid
        self.__key = key
        self.__from = fr
        self.__to = to

    def translate(self, *args) -> list[str]:
        salt = str(random.randint(10000000, 99999999))
        q = '\n'.join([s for s in args])
        sign = hashlib.md5((self.__appid + q + salt + self.__key).encode('utf-8'))
        params = {
            'from': self.__from,
            'to': self.__to,
            'appid': self.__appid,
            'salt': salt,
            'sign': sign.hexdigest(),
            'q': q
        }

        return Translator.__request(self.__api, params)

    @classmethod
    def __request(cls, url: str, params: dict) -> list[str]:
        request_success = False
        retry_time = 0
        retry_limit = int(CONFIG['RETRY'])
        while not request_success and retry_time < retry_limit:
            retry_time += 1
            try:
                resp = requests.get(url, params=params)
                data = resp.json().get('trans_result', [])
                dst = [item.get('dst', '') for item in data]
                request_success = True
            except Exception:
                dst = []

        return dst

