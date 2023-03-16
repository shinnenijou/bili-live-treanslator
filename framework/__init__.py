from tkinter import *
from tkinter import ttk
from .wingui import WinGUI
from .setting import SettingFrame
from .translate import TranslateFrame, StartButton, TextFrame
from multiprocessing import Queue as p_Queue


def run(text_queue: p_Queue):
    win = WinGUI()

    # Style
    setting_style = ttk.Style()
    setting_style.configure('my.TNotebook', tabposition='wn')

    # Tab Manager
    top_tab_manager = ttk.Notebook(win, padding=10)

    # Tabs
    setting_tab = SettingFrame(win)
    translate_tab = TranslateFrame(win)

    # Add Tabs
    top_tab_manager.add(translate_tab, text='翻译', padding=10)
    top_tab_manager.add(setting_tab, text='设置', padding=10)

    # Translate Frame Widgets
    button_commands = [translate_tab.start, translate_tab.stop]
    button_texts = ['Start', 'Stop']
    start_button = StartButton(translate_tab, button_texts, button_commands)
    text_frame = TextFrame(translate_tab, text_queue, width=60, height=10, padx=5, pady=5)

    # Setting Frame Widgets
    setting_tab_manager = ttk.Notebook(setting_tab, style='my.TNotebook')
    global_setting_tab = SettingFrame(setting_tab)
    translate_setting_tab = SettingFrame(setting_tab)
    bilibili_setting_tab = SettingFrame(setting_tab)
    setting_tab_manager.add(global_setting_tab, text='全局', padding=10)
    setting_tab_manager.add(translate_setting_tab, text='翻译', padding=10)
    setting_tab_manager.add(bilibili_setting_tab, text='bili', padding=10)

    # Widgets Position
    top_tab_manager.pack(fill=BOTH, expand=True)
    text_frame.grid(column=0, columnspan=3, row=0)
    start_button.grid(column=2, row=2, pady=10, padx=10)
    setting_tab_manager.pack(fill=BOTH, expand=True)

    win.mainloop()
