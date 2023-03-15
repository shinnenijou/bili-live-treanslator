from tkinter import *
from tkinter import ttk

# global master
root = Tk()

class MainWindow:
    def __init__(self, master, **kwargs):
        title = kwargs.pop('title')
        command = kwargs.pop('command')
        self.button = Button(master, text=title, command=command)
        self.button.config(state=DISABLED)
        self.button.pack()

class PairButton:
    def __init__(self, master, **kwargs):
        title = kwargs.pop('text', '')
        self.button = Button(master, text=title, command=self.on_click)
        self.button.pack()
        self.pairButton = None

    def on_click(self):
        self.config(state=DISABLED)
        self.pairButton.config(state=NORMAL)

    def set_pair(self, button: Button):
        self.pairButton = button

    def config(self, **kwargs):
        self.button.config(**kwargs)


def start_process():
    print("Start...")


def stop_process():
    print("Stop...")



def on_exit():
    print("closing")
    root.destroy()


def run():
    root.protocol("WM_DELETE_WINDOW", on_exit)

    start_button = PairButton(root, text='Start')
    start_button.config(state=NORMAL)
    stop_button = PairButton(root, text='Stop')
    stop_button.config(state=DISABLED)

    start_button.set_pair(stop_button)
    stop_button.set_pair(start_button)

    root.mainloop()