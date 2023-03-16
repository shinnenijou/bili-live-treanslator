from tkinter import *
from tkinter import scrolledtext
from multiprocessing import Queue as p_Queue

import utils


class TextFrame:
    def __init__(self, master, text_queue: p_Queue,**kwargs):
        self.__scrolledtext = scrolledtext.ScrolledText(master, **kwargs)
        self.__text = StringVar(self.__scrolledtext, value='hello')
        self.__scrolledtext.bind()
        self.__queue = text_queue

    def update(self):
        if self.__queue.empty():
            return

        texts = utils.get_all(self.__queue)
        self.__scrolledtext.config(state=NORMAL)
        for text in texts:
            self.__scrolledtext.insert('end', text + '\n')

        self.__scrolledtext.config(state=DISABLED)


