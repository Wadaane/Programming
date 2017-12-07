#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

In this script, we draw an image
on the canvas.

Author: Jan Bodnar
Last modified: July 2017
Website: www.zetcode.com
"""

## pyinstaller -F --noconsole --add-data=logo.png;. tkinter_images_wadaane.py
import tkinter, PIL
from tkinter import Tk, Canvas, Frame, BOTH, NW
from PIL import Image, ImageTk
import sys
import os

class Example(Frame):
  
    def __init__(self):
        super().__init__()   
         
        self.initUI()
        

    def initUI(self):
        self.master.title("Logo")        
        self.pack(fill=BOTH, expand=1)
        
        self.img = Image.open(resource_path("logo.png"))
        self.img = self.img.resize((512,512), Image.ANTIALIAS)
        self.tatras = ImageTk.PhotoImage(self.img)
        canvas = Canvas(self, width=self.img.size[0]+20, 
           height=self.img.size[1]+20)
        canvas.create_image(10, 10, anchor=NW, image=self.tatras)
        canvas.pack(fill=BOTH, expand=1)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
 
def main():
  
    root = Tk()
    ex = Example()
    root.mainloop()  

if __name__ == '__main__':
    main()      