from tkinter import *
from tkinter import ttk
from configparser import RawConfigParser
import utils
from config import Const


class SettingManager(ttk.Notebook):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_setting_tab(self, config: RawConfigParser, text: str = '',**kwargs):
        setting_tab = SettingTab(config, self, **kwargs)
        self.add(setting_tab, text=text)
        return setting_tab

    def get_select(self):
        tab: str = self.select()
        tab = tab[tab.rfind('.') + 1:]

        return self.children[tab]

    def allow_modify(self):
        for _, entry in self.get_select().children.items():
            if not isinstance(entry, SettingValue):
                continue

            entry.config(state=NORMAL)

        return True

    def save_modify(self):
        for _, entry in self.get_select().children.items():
            if not isinstance(entry, SettingValue):
                continue

            entry.config(state=DISABLED)

        return True


class SettingTab(Frame):
    def __init__(self, config: RawConfigParser, master, **kwargs):
        super().__init__(master, **kwargs)

        # config object
        self.__config = config

    def add_option(self, option_name: str = '', value : str = ''):
        label = SettingOption(self, text=option_name)
        entry = SettingValue(self, value, exportselection=0)
        label.value_object = entry
        entry.option_object = label

        return label, entry

    def grid_children(self):
        row = 0
        for _, child in self.children.items():
            if not isinstance(child, SettingOption):
                continue

            child.grid(row=row, column=0, sticky=W)
            child.value_object.grid(row=row, column=1, sticky=E)
            row += 1


class SettingOption(Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.value_object = None


class SettingValue(Entry):
    def __init__(self, master, value: str = '',**kwargs):
        super().__init__(master, **kwargs)
        self.insert('end', value)
        self.__value = value
        self.config(state=DISABLED)
        self.option_object = None

    def set_value(self, value: str):
        self.__value = value

    def reset(self):
        self.config(state=NORMAL)
        self.delete(0, 'end')
        self.insert('end', self.__value)
        self.config(state=DISABLED)
