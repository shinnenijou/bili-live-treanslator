import whisper
import torch
import gc
from multiprocessing import Queue as p_Queue

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

    def run(self):
        while True:
            speech = self.__src_queue.get()
            if speech == '' or not utils.is_file_exist(speech):
                continue

            text = self.__model.transcribe(speech, language='ja')
            for segment in text.get('segments', []):
                temp = segment.get('text', '')
                self.__dst_queue.put(temp)
