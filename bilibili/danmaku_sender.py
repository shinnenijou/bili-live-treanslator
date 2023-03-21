import requests
from requests import exceptions, utils as req_utils
import json
from time import time, sleep
from multiprocessing import Queue as p_Queue
from threading import Thread, Event

import utils
from .enums import *


class DanmakuSender(Thread):
    def __init__(self, _room_id: str,  _src_queue: p_Queue, _dst_queue: p_Queue,
                 _sessdata: str, _bili_jct: str, _buvid3: str, _send_interval: float, timeout=(3.05, 5)):

        super().__init__()
        # requests config
        self.__session = requests.session()
        self.__url = "https://api.live.bilibili.com/msg/send"
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30',
            'Origin': f'https://live.bilibili.com',
            'Referer': f'https://live.bilibili.com/{_room_id}'
        }
        self.__timeout = timeout

        # account config
        self.__room_id = _room_id
        self.__csrf = _bili_jct
        cookie = f'buvid3={_buvid3};SESSDATA={_sessdata};bili_jct={_bili_jct}'
        req_utils.add_dict_to_cookiejar(self.__session.cookies, {"Cookie": cookie})


        # danmaku config
        self.__mode = EDanmakuPosition.Roll
        self.__color = EDanmakuColor.White
        self.__name = ''
        self.__send_interval = _send_interval

        # Control
        self.__is_running = Event()
        self.__src_queue = _src_queue
        self.__dst_queue = _dst_queue

    def init(self):
        if self.get_user_info() == '':
            utils.logger.error("获取用户信息, 请检查配置文件")
            return False

        if self.get_danmaku_config() == (None, None):
            utils.logger.error("获取弹幕配置失败, 请检查配置文件")
            return False

        return True

    def __post(self, url: str, data: dict) -> tuple[ESendResult, requests.Response|None]:
        """
        POST包装方法, 用于捕获异常
        :param url: 请求地址
        :param data: post数据
        :return: 返回结果枚举与响应体
        """
        result = ESendResult.Error
        resp = None
        try:
            resp = self.__session.post(url=url, headers=self.__headers, data=data, timeout=self.__timeout)
            if resp.status_code == EHTTPStatusCode.OK:
                result = ESendResult.Success
            else:
                resp = None
        except exceptions.ConnectionError:
            pass
        except exceptions.Timeout:
            pass

        return result, resp

    def __get(self, url: str, params: dict = None) -> tuple[ESendResult, requests.Response|None]:
        """
        GET包装方法, 用于捕获异常
        :param url: 请求地址
        :param params: 请求参数
        :return: 返回结果枚举与响应体
        """
        result = ESendResult.Error
        resp = None
        try:
            resp = self.__session.get(url=url, headers=self.__headers, params=params, timeout=self.__timeout)
            if resp.status_code == EHTTPStatusCode.OK:
                result = ESendResult.Success
            else:
                resp = None
        except exceptions.ConnectionError:
            pass
        except exceptions.Timeout:
            pass

        return result, resp

    def __send(self, msg: str) -> tuple[ESendResult, dict]:
        data={
            "color": self.__color,
            "fontsize": 25,
            "mode": self.__mode,
            "bubble": 0,
            "msg": msg,
            "roomid": self.__room_id,
            "rnd": int(time()),
            "csrf_token": self.__csrf,
            "csrf": self.__csrf,
        }
        result, resp = self.__post(self.__url, data)
        if result == ESendResult.Success:
            resp = json.loads(resp.text)
            result = resp['code']

        return result, resp

    def send(self, msg: str):
        """
        向直播间发送弹幕
        :param msg: 待发送的弹幕内容
        :return: 服务器返回的响应体
        """
        result, resp = self.__send(msg)
        if result == ESendResult.Success:
            self.__dst_queue.put(msg)
        elif result == ESendResult.DuplicateMsg:
            utils.logger.error("发送失败：重复弹幕")
        else:
            utils.logger.error(f"发送失败：未知错误, 错误代码： {result}")

    def get_name(self):
        return self.__name

    def get_danmaku_config(self):
        """获取用户在直播间内的当前弹幕颜色、弹幕位置、发言字数限制等信息"""
        url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByUser"
        params = {"room_id": self.__room_id}
        result, resp = self.__get(url=url, params=params)
        resp = json.loads(resp.text)
        if result == ESendResult.Success and resp['code'] == ESendResult.Success:
            danmaku_config = resp["data"]["property"]["danmu"]
            self.__mode = danmaku_config["mode"]
            self.__color = danmaku_config["color"]

        return self.__mode, self.__color

    def set_danmu_config(self, color=None, mode=None):
        """设置用户在直播间内的弹幕颜色或弹幕位置
        :（颜色参数为十六进制字符串，颜色和位置不能同时设置）"""
        url = "https://api.live.bilibili.com/xlive/web-room/v1/dM/AjaxSetConfig"
        data = {
            "room_id": self.__room_id,
            "color": color,
            "mode": mode,
            "csrf_token": self.__csrf,
            "csrf": self.__csrf,
        }
        result, resp = self.__post(url=url, data=data)
        resp = json.loads(resp.text)
        if result == ESendResult.Success and resp['code'] == ESendResult.Success:
            self.__mode = mode
            self.__color = color

        return result

    def get_user_info(self):
        """获取用户信息"""
        url = "https://api.bilibili.com/x/space/myinfo"
        result, resp = self.__get(url=url)
        resp = json.loads(resp.text)
        if result == ESendResult.Success and resp['code'] == ESendResult.Success:
            self.__name = resp['data']['name']

        return self.__name

    def update_config(self, room_id: str, sessdata: str, bili_jct: str, buvid3: str, send_interval: float):
        self.__room_id = room_id
        self.__csrf = bili_jct
        cookie = f'buvid3={buvid3};SESSDATA={sessdata};bili_jct={bili_jct}'
        req_utils.add_dict_to_cookiejar(self.__session.cookies, {"Cookie": cookie})
        self.__send_interval = send_interval

    def run(self):
        self.__is_running.set()
        while self.__is_running.is_set():
            text = self.__src_queue.get(block=True)
            if text != '':
                self.send(text)
                sleep(self.__send_interval)

    def stop(self):
        self.__is_running.clear()
        self.__src_queue.put('')

