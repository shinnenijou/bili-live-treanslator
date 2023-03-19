from tkinter import *
from tkinter import ttk
from multiprocessing import Queue as p_Queue

from .wingui import WinGUI
from .setting import SettingTab, SettingManager
from .translate import TranslateFrame, TextFrame
from .button import TransButton

from config import config


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
    setting_tab = Frame(top_tab_manager)


    # Add Tabs
    top_tab_manager.add(translate_tab, text='翻译')
    top_tab_manager.add(setting_tab, text='设置')

    # Translate Frame Direct Widgets
    start_button = TransButton(
        translate_tab,
        ['开始同传', '结束同传'],
        [start_threads, stop_threads]
    )
    text_frame = TextFrame(gui_text_queue, translate_tab, height=10)

    # Setting Frame Direct Widgets
    setting_tab_manager = SettingManager(setting_tab, style='my.TNotebook')
    modify_button = TransButton(
        setting_tab_manager,
        ['修改', '保存'],
        [setting_tab_manager.allow_modify, setting_tab_manager.save_modify]
    )

    # Global Setting
    global_setting = setting_tab_manager.add_setting_tab(config.global_config, text='全局', name='global')
    global_setting.add_option('翻译接口', config.global_config['global']['translator'])

    # Bilibili Setting
    bilibili_setting = setting_tab_manager.add_setting_tab(config.bilibili, text='弹幕', name='bilibili')
    bilibili_setting.add_option('直播间', config.bilibili['room']['target_room'])
    bilibili_setting.add_option('弹幕发送间隔', config.bilibili['room']['send_interval'])
    bilibili_setting.add_option('SESSDATA', config.bilibili['user']['sessdata'])
    bilibili_setting.add_option('BILI_JCT', config.bilibili['user']['bili_jct'])
    bilibili_setting.add_option('BUVID3', config.bilibili['user']['buvid3'])

    # Translate Setting
    translator_name = config.global_config['global']['translator']
    translate_setting = setting_tab_manager.add_setting_tab(config.translate, text='翻译', name='translate')
    translate_setting.add_option('API', config.translate[translator_name]['api'])
    translate_setting.add_option('APPID', config.translate[translator_name]['appid'])
    translate_setting.add_option('KEY', config.translate[translator_name]['key'])
    translate_setting.add_option('源语言', config.translate[translator_name]['from'])
    translate_setting.add_option('目标语言', config.translate[translator_name]['to'])
    translate_setting.add_option('重试次数', config.translate[translator_name]['retry_limit'])

    # Widgets Position
    top_tab_manager.pack(fill=BOTH, expand=True)
    text_frame.pack(fill=BOTH, expand=True)
    start_button.pack(pady=10, padx=10)
    setting_tab_manager.pack(fill=BOTH, expand=True)
    modify_button.pack(side=BOTTOM)

    global_setting.grid_children()
    bilibili_setting.grid_children()
    translate_setting.grid_children()

    win.mainloop()
