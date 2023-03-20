from tkinter import *
from tkinter import ttk
from multiprocessing import Process, Queue as p_Queue
from threading import Thread
import signal
import os

import config
import translator
import bilibili
import utils
import asr

from .setting import *
from .translate import *
from .button import *


class WinGUI(Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # global config
        self.title(config.Const.AppTitle)
        self.geometry(config.Const.AppSize)
        self.resizable(width=False, height=False)
        self.__config = config.GlobalConfig()

        # override sys callback
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Sync Queue
        self.__gui_text_queue = p_Queue(maxsize=0)
        self.__speech_queue = p_Queue(maxsize=0)
        self.__translate_queue = p_Queue(maxsize=0)
        self.__danmaku_send_queue = p_Queue(maxsize=0)

        # logger
        utils.init(self.__gui_text_queue)

        # process
        self.__recognizer_p = Process(target=self.run_recognizer)  # recognizer object will be created in child process

        # thread
        self.__translator = translator.TranslatorMap[self.__config.global_config.get('global', 'translator', 'baidu')](
            _src_queue=self.__translate_queue,
            _dst_queue=self.__danmaku_send_queue,
            _name=self.__config.global_config.get('global', 'translator', 'baidu'),
            _config = self.__config.translate[self.__config.global_config.get('global', 'translator', 'baidu')]
        )
        self.__translator_t = Thread(target=self.__translator.start)

        self.__sender = bilibili.DanmakuSender(
            _room_id=self.__config.bilibili.get('room', 'target_room', ''),
            _src_queue=self.__danmaku_send_queue,
            _dst_queue=self.__gui_text_queue,
            _sessdata=self.__config.bilibili.get('user', 'sessdata', ''),
            _bili_jct=self.__config.bilibili.get('user', 'bili_jct', ''),
            _buvid3=self.__config.bilibili.get('user', 'buvid3', ''),
            _send_interval=self.__config.bilibili.get('room', 'send_interval', '')
        )
        self.__sender_t = Thread(target=self.__sender.start)

        # running flag
        self.__is_running = False

        # start process
        self.__recognizer_p.start()
        if self.__translate_queue.get() != config.EProcessStatus.Ready:
            self.__recognizer_p.join()
            raise RuntimeError('ASR process failed to start!')



    @property
    def config(self):
        return self.__config

    @property
    def gui_text_queue(self):
        return self.__gui_text_queue

    @property
    def speech_queue(self):
        return self.__speech_queue

    @property
    def translate_queue(self):
        return self.__translate_queue

    @property
    def danmaku_send_queue(self):
        return self.__danmaku_send_queue

    @property
    def recognizer_p(self):
        return self.__recognizer_p

    @property
    def translator(self):
        return self.__translator

    @property
    def translator_t(self):
        return self.__translator_t

    @property
    def sender(self):
        return self.__sender

    @property
    def sender_t(self):
        return self.__sender_t

    def on_exit(self):
        os.kill(self.__recognizer_p.pid, signal.SIGINT)

        if self.__is_running:
            self.stop_threads()
            self.__is_running = False

        self.destroy()

    def run_recognizer(self):
        recognizer = asr.ASRRecognizer(
            _model_name=self.__config.global_config.get('global', 'asm_model'),
            _src_queue=self.__speech_queue,
            _dst_queue=self.__translate_queue,
            _gui_text_queue=self.__gui_text_queue
        )

        signal.signal(signal.SIGINT, recognizer.stop)

        if not recognizer.init():
            self.__translate_queue.put(config.EProcessStatus.Error)
            return
        else:
            self.__translate_queue.put(config.EProcessStatus.Ready)

        # Block Here!
        recognizer.start()

    def start_threads(self):
        self.__is_running = True

        # Init translator thread
        if not self.__sender.init():
            self.stop_threads()
            return False

        utils.logger.info('翻译组件初始化完成...')

        # Init danmaku sender thread
        if not self.__sender.init():
            self.stop_threads()
            return False

        utils.logger.info(f'发送组件初始化完成, 用户: {self.__sender.get_name()}')

        # Start Threads
        utils.logger.info('初始化完成, 翻译机开始运行')
        self.__sender_t.start()
        self.__translator.start()

        return True

    def stop_threads(self):
        self.__translator.stop()
        self.__translator_t.join()
        utils.logger.info('成功停止翻译组件...')

        self.__sender.stop()
        self.__sender_t.join()
        utils.logger.info('成功停止发送组件...')

        utils.logger.info('翻译机已停止运行')

        self.__is_running = False

        return True

    def run(self):
        # Style
        # top_style = ttk.Style()
        # top_style.layout('Tabless.TNotebook.Tab', [])

        setting_style = ttk.Style()
        setting_style.configure('my.TNotebook', tabposition='w')

        # Tab Manager
        top_tab_manager = ttk.Notebook(self)

        # Tabs
        translate_tab = TranslateFrame(top_tab_manager)
        setting_tab_manager = SettingManager(top_tab_manager, style='my.TNotebook')

        # Add Tabs
        top_tab_manager.add(translate_tab, text='翻译')
        top_tab_manager.add(setting_tab_manager, text='设置')

        # Translate Frame Direct Widgets
        start_button = TransButton(
            translate_tab,
            ['开始同传', '结束同传'],
            [self.start_threads, self.stop_threads]
        )
        text_frame = TextFrame(self.__gui_text_queue, translate_tab, height=10)

        # Setting Frame Direct Widgets

        # Global Setting
        setting_tab_manager.add_tab(self.__config.global_config, tab_title='全局', name='global')
        global_setting = setting_tab_manager.add_section(tab_name='global', section_title='global', name='global')
        global_setting.add_options(config.GlobalTitleToOption.get('global', {}), self.__config.global_config['global'])

        # Bilibili Setting
        setting_tab_manager.add_tab(self.__config.bilibili, tab_title='弹幕', name='bilibili')
        bilibili_setting = setting_tab_manager.add_section(tab_name='bilibili', section_title='直播间', name='room')
        bilibili_setting.add_options(config.BilibiliTitleToOption.get('room', {}), self.__config.bilibili['room'])
        bilibili_setting = setting_tab_manager.add_section(tab_name='bilibili', section_title='用户', name='user')
        bilibili_setting.add_options(config.BilibiliTitleToOption.get('user', {}), self.__config.bilibili['user'])

        # Translate Setting
        setting_tab_manager.add_tab(self.__config.translate, tab_title='翻译', name='translate')
        translate_setting = setting_tab_manager.add_section(tab_name='translate', section_title='baidu', name='baidu')
        translate_setting.add_options(config.TranslateTitleToOption.get('baidu', {}), self.__config.translate['baidu'])

        # Widgets Position
        top_tab_manager.pack(fill=BOTH, expand=True)
        text_frame.pack(fill=BOTH, expand=True)
        start_button.pack(pady=10, padx=10)

        setting_tab_manager.pack_tabs()

        self.mainloop()



