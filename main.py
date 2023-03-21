import os
from multiprocessing import Process, Queue as p_Queue

import gui
import utils
from config import GlobalConfig, EProcessStatus, TEMP_ROOT
if os.getenv('GUIONLY') is None:
    import asr


def run_recognizer(
        _config: GlobalConfig,
        _gui_text_queue: p_Queue,
        _speech_queue: p_Queue,
        _translate_queue: p_Queue,
        _danmaku_send_queue: p_Queue):

    recognizer = asr.ASRRecognizer(
        _model_name=_config.global_config.get('global', 'asr_model'),
        _src_queue=_speech_queue,
        _dst_queue=_translate_queue,
        _gui_text_queue=_gui_text_queue
    )

    if not recognizer.init():
        _translate_queue.put(EProcessStatus.Error)
        return
    else:
        _translate_queue.put(EProcessStatus.Ready)

    # Block Here!
    recognizer.run()

    exit(0)

def run_recorder():
    pass


if __name__ == '__main__':
    utils.mkdir(TEMP_ROOT)

    gui_text_queue = p_Queue(maxsize=0)
    speech_queue = p_Queue(maxsize=0)
    translate_queue = p_Queue(maxsize=0)
    danmaku_send_queue = p_Queue(maxsize=0)

    config = GlobalConfig()
    if os.getenv('GUIONLY') is None:
        recognizer_p = Process(  # recognizer object will be created in child process
            target=run_recognizer,
            args=(
                config,
                gui_text_queue,
                speech_queue,
                translate_queue,
                danmaku_send_queue,
            )
        )
        recognizer_p.start()

        if translate_queue.get() != EProcessStatus.Ready:
            recognizer_p.join()
            raise RuntimeError('ASR process failed to start!')

    win = gui.WinGUI(
        _config=config,
        _gui_text_queue=gui_text_queue,
        _speech_queue=speech_queue,
        _translate_queue=translate_queue,
        _danmaku_send_queue=danmaku_send_queue
    )
    win.run()

    if os.getenv('GUIONLY') is None:
        recognizer_p.terminate()
        recognizer_p.join()

    utils.remove(TEMP_ROOT)
    exit(0)
