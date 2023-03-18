from tkinter import *
from tkinter import ttk
from configparser import RawConfigParser
import utils
from config import Const


class SettingFrame(Frame):
    def __init__(self, config: RawConfigParser, master, **kwargs):
        super().__init__(master, **kwargs)

        # config object
        self.__config = config

        # register update to mainloop
        self.after(Const.UpdateInterval, self.__update)

    def __update(self):
        self.after(Const.UpdateInterval, self.__update)

    def save_config(self):
        utils.save_config(self.__config)


class SettingOption(Label):
    def __init__(self, master, option: str,**kwargs):
        super().__init__(master, **kwargs)
        self.__option = option
        self.value_object = None

    def set_value_object(self, value_object):
        self.value_object = value_object

    def get_option(self):
        return self.__option

    def get_value(self):
        if self.value_object is None:
            return None

        return self.value_object.get_value()


class SettingValue(Entry):
    def __init__(self, master, value: str = '',**kwargs):
        super().__init__(master, **kwargs)
        self.__value = value
        self.option_object = None

    def set_option_object(self, option_object):
        self.option_object = option_object

    def get_value(self):
        return self.__value

    def get_option(self):
        if self.option_object is None:
            return None

        return self.option_object.get_option()


def make_setting_pair(master, option:str = '', value = ''):
    """
    factory function for setting pair without any widget configure
    :param master:
    :param option:
    :param value:
    :return: (option, value) pair
    """
    label = SettingOption(master, option)
    entry = SettingValue(master, value)
    label.set_value_object(entry)
    entry.set_option_object(label)

    return label, entry
