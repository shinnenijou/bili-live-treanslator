import os
import gui
if os.getenv('GUIONLY') is None:
    import asr

if __name__ == '__main__':
    gui = gui.WinGUI()
    gui.run()