from tkinter import *
from tkinter import ttk,messagebox
from configparser import SectionProxy, RawConfigParser

from .button import TransButton
from config import Config


class SettingManager(ttk.Notebook):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_tab(self, config: RawConfigParser, tab_title: str, **kwargs):
        setting_tab = SettingFrame(self, config,**kwargs)
        self.add(setting_tab, text=tab_title)

        Button(
            setting_tab,
            text='取消',
            command=self.cancel_modify
        )

        TransButton(
            setting_tab,
            ['修改', '保存'],
            [self.allow_modify, self.save_modify]
        )

        return setting_tab

    def add_section(self, tab_name: str, **kwargs):
        setting_tab = self.children.get(tab_name, None)
        if setting_tab is None:
            return

        setting_section = SettingSection(setting_tab, **kwargs)
        return setting_section

    def get_select(self):
        tab: str = self.select()
        tab = tab[tab.rfind('.') + 1:]

        return self.children[tab]

    def allow_modify(self):
        for _, section in self.get_select().children.items():
            if not isinstance(section, SettingSection):
                continue

            for _, entry in section.children.items():
                if not isinstance(entry, SettingValue):
                    continue

                entry.config(state=NORMAL)

        return True

    def save_modify(self):
        if not messagebox.askyesno('保存设置', '是否保存设置?'):
            return

        return self.get_select().update_config()

    def cancel_modify(self):
        for _, section in self.get_select().children.items():
            if not isinstance(section, SettingSection):
                continue

            for _, entry in section.children.items():
                if not isinstance(entry, SettingValue):
                    continue

                entry.reset()

        return True

    def pack_tabs(self):
        for name, widget in self.children.items():
            if not isinstance(widget, SettingFrame):
                continue

            for _, section in widget.children.items():
                if isinstance(section, Button):
                    section.pack(side=BOTTOM)

                if isinstance(section, SettingSection):
                    section.pack(side=TOP)
                    section.grid_children()


class SettingFrame(Frame):

    def __init__(self, master, config: Config, **kwargs):
        super().__init__(master, **kwargs)
        self.row = 0
        self.__config = config

    def update_config(self):
        for section_name, section in self.children.items():
            if not isinstance(section, SettingSection):
                continue

            for option_name, entry in section.children.items():
                if not isinstance(entry, SettingValue):
                    continue

                if entry.update_value():
                    self.__config.set(section_name, option_name, entry.get())
                entry.config(state=DISABLED)

        self.__config.save_config()
        return True


class SettingSection(Frame):
    def __init__(self, master, section_title: str, **kwargs):
        super().__init__(master, **kwargs)
        self.__label = Label(self, text=section_title)

    def add_option(self, title: str, option_name:str, value : str, value_name:str, **kwargs):
        label = SettingOption(self, text=title, name=option_name)
        entry = SettingValue(self, value=value, exportselection=0, name=value_name)
        label.value_object = entry
        entry.option_object = label

        return label, entry

    def add_options(self, options: dict, config: SectionProxy):
        for title, option_name in options.items():
            value = config.get(option_name, '')
            self.add_option(title, '_' + option_name , value, option_name)

    def grid_children(self):
        row = self.master.row
        self.__label.grid(row=row, column=0, columnspan=2, sticky=W)
        row += 1
        for _, child in self.children.items():
            if not isinstance(child, SettingOption):
                continue

            child.grid(row=row, column=0, sticky=W)
            child.value_object.grid(row=row, column=1, sticky=E)
            row += 1
        self.master.row = row


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

    def update_value(self):
        if self.__value == self.get():
            return False

        self.__value = self.get()
        return True

    def reset(self):
        self.config(state=NORMAL)
        self.delete(0, 'end')
        self.insert('end', self.__value)
        self.config(state=DISABLED)
