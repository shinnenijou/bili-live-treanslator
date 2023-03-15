from tkinter import *
from tkinter import ttk


class PairButton:
    def __init__(self, master, text, command, column, row):
        self.button = Button(master, text=text, command=self.on_click)

        self.command = command
        self.pairButton = None

        self.button.grid(column=column, row=row)

    def on_click(self):
        self.command()

        self.set_inactive()
        self.pairButton.set_active()

    def set_pair(self, button: Button):
        self.pairButton = button

    def set_active(self):
        self.__config(state=NORMAL)

    def set_inactive(self):
        self.__config(state=DISABLED)

    def __config(self, **kwargs):
        self.button.config(**kwargs)