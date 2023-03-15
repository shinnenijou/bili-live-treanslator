from tkinter import *


class MainWindow(Tk):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_exit(self):
        print("closing")
        self.destroy()

    @staticmethod
    def start_process():
        print("Start...")

    @staticmethod
    def stop_process():
        print("Stop...")