from tkinter import *
from tkinter import ttk
from multiprocessing import Queue as p_Queue
from configparser import RawConfigParser

from .wingui import WinGUI
from .setting import SettingFrame
from .translate import TranslateFrame, StartButton, TextFrame

import bilibili
import translator
from config import CONFIG_ROOT, ConfigFile, EConfigType


CONFIG = RawConfigParser()
CONFIG.read(CONFIG_ROOT + ConfigFile[EConfigType.Global])


def init():
    pass


def run(gui_text_queue, start_process, stop_process):
    win = WinGUI(stop_process)

    # Style
    #top_style = ttk.Style()
    #top_style.layout('Tabless.TNotebook.Tab', [])

    setting_style = ttk.Style()
    setting_style.configure('my.TNotebook', tabposition='wn')

    # Tab Manager
    top_tab_manager = ttk.Notebook(win)

    # Tabs
    setting_tab = Frame(win)
    translate_tab = TranslateFrame(win)

    # Add Tabs
    top_tab_manager.add(translate_tab, text='翻译')
    top_tab_manager.add(setting_tab, text='设置')

    # Translate Frame Widgets
    button_commands = [start_process, stop_process]
    button_texts = ['Start', 'Stop']
    start_button = StartButton(translate_tab, button_texts, button_commands)
    text_frame = TextFrame(gui_text_queue, translate_tab, height=10)

    # Setting Frame Widgets
    setting_tab_manager = ttk.Notebook(setting_tab, style='my.TNotebook')
    global_setting_tab = SettingFrame(CONFIG, setting_tab)
    translate_setting_tab = SettingFrame(translator.CONFIG, setting_tab)
    bilibili_setting_tab = SettingFrame(bilibili.CONFIG, setting_tab)
    setting_tab_manager.add(global_setting_tab, text='全局')
    setting_tab_manager.add(translate_setting_tab, text='翻译')
    setting_tab_manager.add(bilibili_setting_tab, text='bili')

    # Widgets Position
    top_tab_manager.pack(fill=BOTH, expand=True)
    text_frame.pack(fill=BOTH, expand=True)
    start_button.pack(pady=10, padx=10)
    setting_tab_manager.pack(fill=BOTH, expand=True)

    win.mainloop()
