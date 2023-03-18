from tkinter import *
from config import Const


class WinGUI(Tk):
    def __init__(self, stop_process, **kwargs):
        super().__init__(**kwargs)

        # global config
        self.title(Const.AppTitle)
        self.geometry(Const.AppSize)
        self.resizable(width=False, height=False)

        # runtime flag
        self.__PROCESS_FLAG = False
        self.__children = []

        # override sys callback
        self.__command = stop_process
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # register update to mainloop
        self.after(Const.UpdateInterval, self.__update)

    def on_exit(self):
        if callable(self.__command):
            self.__command()

        self.destroy()

    def __update(self):
        self.after(Const.UpdateInterval, self.__update)
