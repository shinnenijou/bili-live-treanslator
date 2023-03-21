import requests
import json
import aiohttp
from threading import Thread, Event
import asyncio
from multiprocessing import Queue as p_Queue

import utils
from config import TEMP_ROOT


class Recorder(Thread):
    def __init__(self, _room_id: str, _dst_queue: p_Queue):
        super().__init__()
        self.__room_id = _room_id
        self.__url = ""
        self.__is_running = Event()
        self.__dst_queue = _dst_queue

    def is_streaming(self):
        api = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={self.__room_id}&from=room"
        try:
            resp = requests.get(api)
        except (requests.ConnectTimeout, requests.ConnectionError):
            return False

        if resp.status_code != 200:
            return False

        live_info = json.loads(resp.text)
        status = live_info.get('data', {}).get('live_status', 0)

        return status == 1

    def init(self):
        self.__url = self.__get_stream_url()
        if not self.__url:
            return False

        return True

    def __get_stream_url(self):
        """获取直播间信息"""
        api = "https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl"
        params = {
            "cid": self.__room_id,
            "platform": "web",
            "qn": 10000,  # int: 清晰度编号，原画 10000，蓝光 400，超清 250，高清 150，流畅 80
            "https_url_req": 1,
            "ptype": 8
        }

        try:
            resp = requests.get(api, params)
        except (requests.ConnectTimeout, requests.ConnectionError):
            return ""

        if resp.status_code != 200:
            return ""

        resp = resp.json()
        url = ""
        if resp['code'] == 0:
            url = resp.get('data', {}).get('durl', [])[0].get('url', "")

        return url

    async def __record(self):
        self.__is_running.set()
        file_index = 1
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60 * 60 * 24, sock_read=10)
        ) as session:
            while self.__is_running.is_set() and self.is_streaming():
                async with session.get(self.__url,  headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}) as resp:
                    with open(f'{TEMP_ROOT}{file_index}.flv', 'ab') as file:
                        while self.__is_running.is_set():
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                self.__dst_queue.put(f'{TEMP_ROOT}{file_index}.flv')
                                file.close()
                                file_index += 1
                                break

                            file.write(chunk)
                            if file.tell() > 1024 * 1024 * 10:
                                self.__dst_queue.put(f'{TEMP_ROOT}{file_index}.flv')
                                file.close()
                                file_index += 1
                                break

    def run(self):
        utils.remove(TEMP_ROOT)
        utils.mkdir(TEMP_ROOT)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__record())
        loop.close()

    def stop(self):
        self.__is_running.clear()