import config
import translator
import bilibili
import stream

from .setting import *
from .translate import *
from .button import *


class WinGUI(Tk):
    def __init__(self,
                 _config: config.GlobalConfig,
                 _gui_text_queue: p_Queue,
                 _speech_queue: p_Queue,
                 _translate_queue: p_Queue,
                 _danmaku_send_queue: p_Queue,
                 _recognizer_pid: int,
                 **kwargs):

        super().__init__(**kwargs)

        # global config
        self.title(config.Const.AppTitle)
        self.geometry(config.Const.AppSize)
        self.resizable(width=False, height=False)
        self.__config = _config

        # override sys callback
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Sync Queue
        self.__gui_text_queue = _gui_text_queue
        self.__speech_queue = _speech_queue
        self.__translate_queue = _translate_queue
        self.__danmaku_send_queue = _danmaku_send_queue

        # logger
        utils.init(self.__gui_text_queue)

        # process
        self.__recognizer_pid = _recognizer_pid

        # thread
        self.__translator = None
        self.__sender = None
        self.__recorder = None

        # Threads running flag
        self.__is_running = False

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
    def translator(self):
        return self.__translator

    @property
    def sender(self):
        return self.__sender

    def on_exit(self):
        if self.__is_running:
            self.stop_threads()
            self.__is_running = False

        self.destroy()

    def start_threads(self):
        self.__is_running = True
        self.__translator = None
        self.__sender = None
        self.__recorder = None

        # Create threads
        translator_name = self.__config.global_config.get('global', 'translator') or 'baidu'
        self.__translator = translator.TranslatorMap[translator_name](
            _src_queue=self.__translate_queue,
            _dst_queue=self.__danmaku_send_queue,
            _name=translator_name,
            _config=self.__config.translate[translator_name],
        )

        if not self.__translator.init():
            self.__translator = None
            return False

        utils.logger.info('翻译组件初始化完成...')

        self.__sender = bilibili.DanmakuSender(
            _room_id=self.__config.bilibili.get('room', 'target_room'),
            _src_queue=self.__danmaku_send_queue,
            _dst_queue=self.__gui_text_queue,
            _sessdata=self.__config.bilibili.get('user', 'sessdata'),
            _bili_jct=self.__config.bilibili.get('user', 'bili_jct'),
            _buvid3=self.__config.bilibili.get('user', 'buvid3'),
            _send_interval=self.__config.bilibili.get('room', 'send_interval')
        )

        # Init danmaku sender thread
        if not self.__sender.init():
            self.__translator = None
            self.__sender = None
            return False

        utils.logger.info(f'发送组件初始化完成, 用户: {self.__sender.get_name()}')

        self.__recorder = stream.Recorder(
            _room_id=self.__config.bilibili.get('room', 'target_room'),
            _dst_queue=self.__speech_queue,
            cookies={
                "sessdata": self.__config.bilibili.get('user', 'sessdata'),
                "bili_jct": self.__config.bilibili.get('user', 'bili_jct'),
                "buvid3": self.__config.bilibili.get('user', 'buvid3'),
            }
        )

        if not self.__recorder.init():
            self.__translator = None
            self.__sender = None
            self.__recorder = None
            return False

        utils.logger.info(f'流媒体组件初始化完成')

        self.__speech_queue.put('clear')

        # Start Threads
        utils.logger.info('初始化完成, 翻译机开始运行')
        self.__sender.start()
        self.__translator.start()
        self.__recorder.start()

        return True

    def stop_threads(self):
        if self.__translator is not None:
            self.__translator.stop()
            self.__translator.join()
            utils.logger.info('成功停止翻译组件...')

        if self.__sender:
            self.__sender.stop()
            self.__sender.join()
            utils.logger.info('成功停止发送组件...')

        if self.__recorder:
            self.__recorder.stop()
            self.__recorder.join()
            utils.logger.info('成功停止流媒体组件...')

        utils.logger.info('翻译机已停止运行')

        self.__is_running = False
        self.__translator = None
        self.__sender = None
        self.__recorder = None

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



