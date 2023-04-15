import math
import gc
import os
from multiprocessing import Queue as p_Queue

from faster_whisper import WhisperModel

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
        self.__model = None

    def init(self):
        if not utils.isdir(MODEL_ROOT + self.__model_name):
            return False

        self.__model = WhisperModel(
            model_size_or_path=MODEL_ROOT + self.__model_name
        )

        return True

    def restart(self, *args, **kwargs):
        pass

    def config_update(self, model_name: str):
        if model_name == self.__model_name:
            return

        self.__model_name = model_name

        self.__model = WhisperModel(
            model_size_or_path=MODEL_ROOT + self.__model_name
        )

        gc.collect()

    def run(self):
        while True:
            file = self.__src_queue.get()
            if file == '' or not utils.isfile(file):
                continue

            if file == 'clear':
                continue

            audio_file = utils.transcode_to_audio(file)
            utils.rm(file)

            if not utils.isfile(audio_file):
                continue

            segments, _ = self.__model.transcribe(
                audio_file,
                language='ja',
                word_timestamps=False,
                vad_filter=True,
            )

            for segment in segments:
                text = utils.anti_recognize.preprocess(segment.text)
                self.__dst_queue.put(text)

            utils.rm(audio_file)
