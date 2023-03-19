from tkinter import *
from .enums import *


class TransButton(Button):
    def __init__(self, master, texts, commands, **kwargs):
        super().__init__(master, **kwargs)
        self.__commands = commands
        self.__texts = texts
        self.config(command=self.__on_click)

        self.__state = EStartButtonState.Start
        self.__update_config()

    def __on_click(self):
        if self.__commands[self.__state]():
            self.__state = EStartButtonState.Stop - self.__state
            self.__update_config()

    def __update_config(self):
        self.config(text=self.__texts[self.__state])