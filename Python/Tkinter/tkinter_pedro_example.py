import os
from tkinter import *

import tkinter_pedro as pedro


# Needed for Pyinstaller's executable to retrieve file from system temporary folder.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def callback(*args):
    angle_base, angle_forearm, angle_hand = canvas.angles.get().split()
    print('Base: {}\n'
          'Forearm: {}\n'
          'Hand: {}\n'.format(angle_base.split('.')[0], angle_forearm.split('.')[0], angle_hand.split('.')[0]))


root = Tk()
root.title("Pedro")
root.iconbitmap(default=resource_path('icon.ico'))
# root.geometry('800x600')
# root.resizable(False, False)
root.bind("<Escape>", lambda e: root.quit())

message = Label(root, text="Click and Drag to move")
message.pack()  # side=BOTTOM

canvas = pedro.TkinterPedro(unit=75, callback=callback,
                            range_hand=(45, 160),
                            range_forearm=(10, 160),
                            range_base=(98, 160))
canvas.pack(expand=False, fill=NONE)

mainloop()
