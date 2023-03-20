from tkinter import *
from tkinter import ttk
from multiprocessing import Queue as p_Queue

from .wingui import WinGUI
from .setting import SettingManager
from .translate import TranslateFrame, TextFrame
from .button import TransButton

from config import config, TranslateTitleToOption, BilibiliTitleToOption, GlobalTitleToOption


def init():
    return True


def run(gui_text_queue: p_Queue, start_threads: p_Queue, stop_threads: p_Queue, destroy_processes):
    win = WinGUI(destroy_processes)

    # Style
    #top_style = ttk.Style()
    #top_style.layout('Tabless.TNotebook.Tab', [])

    setting_style = ttk.Style()
    setting_style.configure('my.TNotebook', tabposition='w')

    # Tab Manager
    top_tab_manager = ttk.Notebook(win)

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
        [start_threads, stop_threads]
    )
    text_frame = TextFrame(gui_text_queue, translate_tab, height=10)

    # Setting Frame Direct Widgets



    # Global Setting
    setting_tab_manager.add_tab(tab_title='全局', name='global')
    global_setting = setting_tab_manager.add_section(tab_name='global', section_title='global', name='global')
    global_setting.add_options(GlobalTitleToOption.get('global', {}), config.global_config['global'])

    # Bilibili Setting
    setting_tab_manager.add_tab(tab_title='弹幕', name='bilibili')
    bilibili_setting = setting_tab_manager.add_section(tab_name='bilibili', section_title='直播间', name='room')
    bilibili_setting.add_options(BilibiliTitleToOption.get('room', {}), config.bilibili['room'])
    bilibili_setting = setting_tab_manager.add_section(tab_name='bilibili', section_title='用户', name='user')
    bilibili_setting.add_options(BilibiliTitleToOption.get('user', {}), config.bilibili['user'])

    # Translate Setting
    setting_tab_manager.add_tab(tab_title='翻译', name='translate')
    translate_setting = setting_tab_manager.add_section(tab_name='translate', section_title='baidu', name='baidu')
    translate_setting.add_options(TranslateTitleToOption.get('baidu', {}), config.translate['baidu'])

    # Widgets Position
    top_tab_manager.pack(fill=BOTH, expand=True)
    text_frame.pack(fill=BOTH, expand=True)
    start_button.pack(pady=10, padx=10)

    setting_tab_manager.pack_tabs()

    win.mainloop()
