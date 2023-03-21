import ffmpeg
import streamlink
from multiprocessing import Process
import requests
import json


class Recorder(Process):
    def __init__(self, room_id: str):
        super().__init__()
        self.__room_id = room_id

    def is_streaming(self):
        api = f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={self.__room_id}&from=room"
        headers = {"Connection": "close"}
        try:
            resp = requests.get(api, headers)
        except (requests.ConnectTimeout, requests.ConnectionError):
            return False

        if resp.status_code != 200:
            return False

        live_info = json.loads(resp.text)
        status = live_info.get('data', {}).get('live_status', 0)

        return status == 1

    def run(self):
        while self.is_streaming():
            stream = streamlink.streams('https://live.bilibili.com/' + self.__room_id)
            print(stream)

    def stop(self):
        self.__is_running = False