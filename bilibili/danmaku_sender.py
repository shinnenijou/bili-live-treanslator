import requests
from requests import exceptions, utils as req_utils
import json
from time import time

import utils
from .bilibili_enum import *
from queue import Queue as t_Queue
import threading


class DanmakuSender:
    """弹幕发送机"""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, room_id: str,  send_queue: t_Queue, show_queue: t_Queue,
                 sessdata: str, bili_jct: str, buvid3: str, timeout=(3.05, 5)):

        # requests config
        self.__session = requests.session()
        self.__url = "https://api.live.bilibili.com/msg/send"
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30',
            'Origin': f'https://live.bilibili.com',
            'Referer': f'https://live.bilibili.com/{room_id}'
        }
        self.__timeout = timeout

        # account config
        self.__room_id = room_id
        self.__csrf = bili_jct
        cookie = f'buvid3={buvid3};SESSDATA={sessdata};bili_jct={bili_jct}'
        req_utils.add_dict_to_cookiejar(self.__session.cookies, {"Cookie": cookie})


        # danmaku config
        self.__mode = EDanmakuPosition.Roll
        self.__color = EDanmakuColor.White
        self.__name = ''

        # Control
        self.__is_running = False
        self.__send_queue = send_queue
        self.__show_queue = show_queue

    def __post(self, url: str, data: dict) -> tuple[ESendResult, requests.Response|None]:
        """
        POST包装方法, 用于捕获异常
        :param url: 请求地址
        :param data: post数据
        :return: 返回结果枚举与响应体
        """
        result = ESendResult.SendFail
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
        result = ESendResult.SendFail
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
        if result != ESendResult.SendFail:
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
            self.__show_queue.put(utils.hms_time() + '|' + msg)
        elif result == ESendResult.DuplicateMsg:
            self.__show_queue.put(utils.hms_time() + '|发送失败：重复弹幕')
        else:
            self.__show_queue.put(utils.hms_time() + '|发送失败：未知错误, 错误代码：' + str(result))


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

    def update_config(self, room_id: str, sessdata: str, bili_jct: str, buvid3: str):
        self.__room_id = room_id
        self.__csrf = bili_jct
        cookie = f'buvid3={buvid3};SESSDATA={sessdata};bili_jct={bili_jct}'
        req_utils.add_dict_to_cookiejar(self.__session.cookies, {"Cookie": cookie})

    def run(self):
        self.__is_running = True
        while self.__is_running:
            text = self.__send_queue.get(block=True)
            if text == '':
                self.send(text)

    def stop(self):
        self.__is_running = False
        self.__send_queue.put('')

