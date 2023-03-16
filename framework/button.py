from tkinter import *
from tkinter import ttk


class StartButton(Button):
    def __init__(self, master, reverse, **kwargs):
        super().__init__(master, **kwargs)
        self.__command = kwargs.pop('command', lambda: None)
        self.config(command=self.__on_click)
        self.__reverse = reverse

        self.__update_state()

    def __on_click(self):
        self.__command()
        self.__update_state()

    def __update_state(self):
        flag = getattr(self.master, 'get_flag', lambda: False)()

        if self.__reverse:
            flag = not flag

        if flag:
            self.config(state=NORMAL)
        else:
            self.config(state=DISABLED)