import os

import requests
from requests import exceptions
import random
import hashlib
from multiprocessing import Queue as p_Queue
from configparser import RawConfigParser, SectionProxy
from threading import Thread, Event

import utils
from .enums import EResult


class BaiduTranslator(Thread):
    def __init__(self, _src_queue: p_Queue, _dst_queue: p_Queue, _name: str, _config: SectionProxy):
        super().__init__()
        
        self.__name = _name

        # Sync Queue
        self.__src_queue = _src_queue
        self.__dst_queue = _dst_queue

        # Request Config
        self.__api = _config['API']
        self.__appid = _config['APPID']
        self.__key = _config['KEY']
        self.__from = _config['FROM']
        self.__to = _config['TO']
        self.__retry_limit = _config['RETRY_LIMIT']

        # Control
        self.__is_running = Event()

    def init(self):
        if not self.validate_config():
            utils.logger.error("[error]翻译器配置错误, 请检查翻译器设置")
            return False

        return True

    def __get(self, _params: dict = None):
        result = EResult.ERROR
        resp = None
        try:
            resp = requests.get(self.__api, params=_params)
            if resp.status_code == 200:
                result = EResult.SUCCESS
                resp = resp.json()
            else:
                resp = None
        except exceptions.ConnectionError:
            pass
        except exceptions.Timeout:
            pass

        return result, resp

    def translate(self, *args):
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

        result, data = self.__get(params)
        if result != EResult.SUCCESS:
            return result, []

        return int(data.get('error_code', 0)), [item.get('dst', '') for item in data.get('trans_result', [])]

    def validate_config(self):
        result, _ = self.translate('')
        return result == EResult.EMPTYPARAM

    def run(self):
        self.__is_running.set()

        while self.__is_running.is_set():
            src_text = utils.get_all(self.__src_queue)

            while src_text.count('') > 0:
                src_text.remove('')

            _, dst_text = self.translate(*src_text)
            if os.getenv('DEBUG', '0') == '1':
                for text in src_text:
                    self.__dst_queue.put(text)

            for text in dst_text:
                self.__dst_queue.put(text)

    def stop(self):
        self.__is_running.clear()
        self.__src_queue.put('')

    def update_config(self, _config: SectionProxy):
        self.__api = _config['API']
        self.__appid = _config['APPID']
        self.__key = _config['KEY']
        self.__from = _config['FROM']
        self.__to = _config['TO']
        self.__retry_limit = _config['RETRY_LIMIT']

    def get_name(self):
        return self.__name
