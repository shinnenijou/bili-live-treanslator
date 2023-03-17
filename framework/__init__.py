from tkinter import *
from tkinter import ttk
from .wingui import WinGUI
from .setting import SettingFrame
from .translate import TranslateFrame, StartButton, TextFrame
from multiprocessing import Queue as p_Queue
from config import EConfigType


def run(text_queue: p_Queue):
    win = WinGUI()

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
    button_commands = [translate_tab.start, translate_tab.stop]
    button_texts = ['Start', 'Stop']
    start_button = StartButton(translate_tab, button_texts, button_commands)
    text_frame = TextFrame(translate_tab, text_queue, height=10)

    # Setting Frame Widgets
    setting_tab_manager = ttk.Notebook(setting_tab, style='my.TNotebook')
    global_setting_tab = SettingFrame(EConfigType.Global, setting_tab)
    translate_setting_tab = SettingFrame(EConfigType.Translate, setting_tab)
    bilibili_setting_tab = SettingFrame(EConfigType.Bilibili, setting_tab)
    setting_tab_manager.add(global_setting_tab, text='全局')
    setting_tab_manager.add(translate_setting_tab, text='翻译')
    setting_tab_manager.add(bilibili_setting_tab, text='bili')

    # Widgets Position
    top_tab_manager.pack(fill=BOTH, expand=True)
    text_frame.pack(fill=BOTH, expand=True)
    start_button.pack(pady=10, padx=10)
    setting_tab_manager.pack(fill=BOTH, expand=True)

    win.mainloop()
