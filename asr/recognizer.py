import math
import gc
import os
from multiprocessing import Queue as p_Queue

import whisper
import torch
import ffmpeg
from whisper.audio import SAMPLE_RATE
import numpy as np

import utils
from config import MODEL_ROOT


class ASRRecognizer(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, _model_name: str, _src_queue: p_Queue, _dst_queue: p_Queue, _gui_text_queue: p_Queue):
        self.__model_name = _model_name
        self.__src_queue = _src_queue
        self.__dst_queue = _dst_queue
        self.__gui_text_queue = _gui_text_queue
        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.__model = None

        self.__buffer = b''
        self.__buffer_threshold = SAMPLE_RATE * 2 * 5

    def init(self):
        if not utils.is_file_exist(MODEL_ROOT + self.__model_name + '.pt'):
            return False

        if self.__model_name not in whisper.available_models():
            return False

        self.__model = whisper.load_model(
            name=self.__model_name,
            device=self.__device,
            download_root=MODEL_ROOT,
            in_memory=True
        )

        return True

    def restart(self, *args, **kwargs):
        self.__buffer = b''

    def config_update(self, model_name: str):
        if model_name == self.__model_name:
            return

        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.__model = whisper.load_model(
            name=model_name,
            device=self.__device,
            download_root=MODEL_ROOT,
            in_memory=True
        )
        gc.collect()

    def load_audio(self, audio_path: str):
        if os.getenv('DEBUG', '0') == '1':
            print('load_audio: ' + audio_path)

        try:
            out, _ = (
                ffmpeg.input(audio_path, threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=SAMPLE_RATE)
                .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
            )
            utils.rm(audio_path)
        except ffmpeg.Error as e:
            print('load_audio error: ', str(e))
            out = b''

        self.__buffer = self.__buffer + out

    def run(self):
        while True:
            file = self.__src_queue.get()
            if file == '' or not utils.is_file_exist(file):
                continue

            if file == 'clear':
                self.__buffer = b''
                continue

            # self.load_audio(file)
            # if len(self.__buffer) < self.__buffer_threshold:
            #     continue
            # buffer_size = len(self.__buffer) - (len(self.__buffer) % 4)
            # data = np.frombuffer(self.__buffer[:buffer_size], np.int16).flatten().astype(np.float32) / 32768.0

            segments = self.__model.transcribe(file, language='ja', word_timestamps=False).get('segments', [])
            for i in range(len(segments)):
                self.__dst_queue.put(segments[i].get('text', ''))

            # seek = buffer_size
            # if len(segments) > 0 and segments[-1].get('text', '') != '':
            # seek = math.ceil(segments[-1].get('start') * SAMPLE_RATE * 2)

            # self.__buffer = self.__buffer[seek:]
