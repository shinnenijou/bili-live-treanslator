from tkinter import *
from tkinter import ttk
from configparser import SectionProxy

from .button import TransButton


class SettingManager(ttk.Notebook):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_tab(self, tab_title: str, **kwargs):
        setting_tab = SettingFrame(self, **kwargs)
        self.add(setting_tab, text=tab_title)

        cancel_button = Button(
            setting_tab,
            text='取消',
            command=self.cancel_modify
        )

        modify_button = TransButton(
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
        for _, section in self.get_select().children.items():
            if not isinstance(section, SettingSection):
                continue

            for _, entry in section.children.items():
                if not isinstance(entry, SettingValue):
                    continue

                entry.config(state=DISABLED)

        return True

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

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.row = 0


class SettingSection(Frame):
    def __init__(self, master, section_title: str, **kwargs):
        super().__init__(master, **kwargs)
        self.__label = Label(self, text=section_title)

    def add_option(self, option_title: str = '', value : str = '', **kwargs):
        label = SettingOption(self, text=option_title, **kwargs)
        entry = SettingValue(self, value=value, exportselection=0, **kwargs)
        label.value_object = entry
        entry.option_object = label

        return label, entry

    def add_options(self, options: dict, config: SectionProxy):
        for title, option_name in options.items():
            value = config.get(option_name, '')
            self.add_option(title, value)

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
