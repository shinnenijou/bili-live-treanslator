from tkinter import *
from tkinter import ttk
from .wingui import WinGUI
from .setting import SettingFrame
from .translate import TranslateFrame, StartButton


def run():
    win = WinGUI()

    # Setting Frame
    setting_frame = SettingFrame(win)

    # Translate Frame
    translate_frame = TranslateFrame(win)

    # Tab Manager
    tab_manager = ttk.Notebook(win)
    tab_manager.add(translate_frame, text='翻译')
    tab_manager.add(setting_frame, text='设置')

    tab_manager.pack(fill=BOTH, expand=True)

    # button
    button_commands = [translate_frame.start, translate_frame.stop]
    button_texts = ['Start', 'Stop']
    start_button = StartButton(translate_frame, button_texts, button_commands)
    start_button.grid(column=0, row=0)

    # NoteBook

    win.mainloop()
