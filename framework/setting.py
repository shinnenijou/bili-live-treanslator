from tkinter import *
from tkinter import ttk
from configparser import ConfigParser, RawConfigParser


class SettingFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # register update to mainloop
        self.after(100, self.__update)

    def __update(self):
        self.after(100, self.__update)
