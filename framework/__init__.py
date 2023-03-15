from tkinter import *
from tkinter import ttk, scrolledtext
from .button import PairButton
from .window import MainWindow


def run():
    app = MainWindow('同传鸡')
    app.geometry('480x270')

    frame = Frame(app)
    frame.grid(column=0, columnspan=320, row=0, rowspan=180)

    # Button
    start_button = PairButton(frame, 'Start', app.start_process, 0, 100)
    stop_button = PairButton(frame, 'Stop', app.stop_process, 0, 150)
    start_button.set_pair(stop_button)
    stop_button.set_pair(start_button)
    start_button.set_active()
    stop_button.set_inactive()

    # ScrolledText
    txt = scrolledtext.ScrolledText(frame, width=40, height=10, state=DISABLED)
    txt.grid(column=0, row=0)

    window.mainloop()
