from tkinter import *
from tkinter import ttk, scrolledtext
from configparser import ConfigParser, RawConfigParser
from .enums import *
from multiprocessing import Queue as p_Queue
import utils


class TranslateFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # register update to mainloop
        self.after(100, self.__update)

        self.__PROCESS_FLAG = False

    def __update(self):
        self.after(100, self.__update)

        if self.__PROCESS_FLAG:
            pass

    def get_flag(self):
        return self.__PROCESS_FLAG

    def start(self):
        if self.__PROCESS_FLAG:
            return

        print("Start")
        self.__PROCESS_FLAG = True

    def stop(self):
        if not self.__PROCESS_FLAG:
            return

        print("Stop")
        self.__PROCESS_FLAG = False


class StartButton(Button):
    def __init__(self, master, texts, commands, **kwargs):
        super().__init__(master, **kwargs)
        self.__commands = commands
        self.__texts = texts
        self.config(command=self.__on_click)

        self.__state = EStartButtonState.Start
        self.__update_config()

    def __on_click(self):
        self.__commands[self.__state]()
        self.__state = EStartButtonState.Stop - self.__state
        self.__update_config()

    def __update_config(self):
        self.config(text=self.__texts[self.__state])


class TextFrame(scrolledtext.ScrolledText):
    def __init__(self, master, text_queue: p_Queue, **kwargs):
        super().__init__(master, **kwargs)
        self.__queue = text_queue
        self.config(state=DISABLED)
        self.after(100, self.__update())

    def __update(self):
        if self.__queue.empty():
            return

        texts = utils.get_all(self.__queue)
        self.config(state=NORMAL)
        for text in texts:
            self.insert('end', text + '\n')

        self.config(state=DISABLED)
