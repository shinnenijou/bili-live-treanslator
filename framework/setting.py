from tkinter import *
from tkinter import ttk
from configparser import ConfigParser, RawConfigParser
import utils
from config import EConfigType, ConfigFile, CONFIG_ROOT, Const


class SettingFrame(Frame):
    def __init__(self, config_type: EConfigType, master, **kwargs):
        super().__init__(master, **kwargs)

        # ini config file
        self.__config = {}
        self.__config_file = CONFIG_ROOT + ConfigFile[config_type]
        utils.touch(self.__config_file)
        self.__init_config()

        # register update to mainloop
        self.after(Const.UpdateInterval, self.__update)

    def __update(self):
        self.after(Const.UpdateInterval, self.__update)

    def __init_config(self):
        self.__config = RawConfigParser()
        self.__config.read(self.__config_file)

