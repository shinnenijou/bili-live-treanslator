import requests
import ffmpeg

# api = "https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo"
# params = {
#     'room_id': 22491717,
#     'protocol': "0,1",
#     'format': '0,1,2',
#     'codec': '0,1',
#     'qn': 10000,
#     'platform': 'web',
#     'ptype': 8
# }
#
# data = requests.get(url=api, params=params).json()
#
# result = ""
#
# if data.get('data').get('live_status') == 1:
#     # living
#     for stream in data.get('data', {}).get('playurl_info', {}).get('playurl', {}).get('stream', []):
#         if stream.get('protocol_name', '') != 'http_stream':
#             continue
#
#         codec = stream.get('format', [])[0].get('codec', {})[0]
#         result = codec.get('url_info', [])[0].get('host', '') + \
#                  codec.get('base_url', '') + \
#                  codec.get('url_info', [])[0].get('extra', '')
#
#         break
#
# ffmpeg.input(result).output('test.flv').run()

from bilibili_api import live, sync
import aiohttp


async def main():
    # 初始化
    room = live.LiveRoom(3)
    # 获取直播流链接
    stream_info = await room.get_room_play_url()
    url = stream_info['durl'][0]['url']



sync(main())