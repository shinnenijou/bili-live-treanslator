from tkinter import *


class WinGUI(Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # global config
        self.title('同传鸡')
        self.geometry('480x270')
        self.resizable(width=False, height=False)

        # runtime flag
        self.__PROCESS_FLAG = False
        self.__children = []

        # override sys callback
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # register update to mainloop
        self.after(100, self.__update)

    def on_exit(self):
        self.destroy()

    def __update(self):
        self.after(100, self.__update)
