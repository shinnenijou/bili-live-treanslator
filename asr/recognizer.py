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

    def __init__(self, _model_name: str, _speech_queue: p_Queue, _translate_queue: p_Queue, _gui_text_queue: p_Queue):
        self.__model_name = _model_name
        self.__speech_queue = _speech_queue
        self.__translate_queue = _translate_queue
        self.__gui_text_queue = _gui_text_queue
        self.__device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.__model = whisper.load_model(
            name=_model_name,
            device=self.__device,
            download_root=MODEL_ROOT,
            in_memory=True
        )

        # Control
        self.__is_running = False

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

    def start(self):
        self.__is_running = True
        while self.__is_running:
            speech = self.__speech_queue.get()
            if speech == '' or not utils.is_file_exist(speech):
                continue

            text = self.__model.transcribe(speech)
            for segment in text.get('segments', []):
                temp = segment.get('text', '')
                self.__translate_queue.put(temp)

    def stop(self):
        self.__is_running = False
        self.__speech_queue.put('')
