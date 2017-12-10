import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


root = Tk()
root.iconbitmap(default=resource_path('icon.ico'))
Title = root.title("Rename Files")
msg_old = StringVar()
msg_old.set("Old")
msg_new = StringVar()
msg_new.set("New")
files = []
pattern = ''
new_names = []
path = ''
_width = 0
_height = 0
temp = ''


def open_directory():
    global path
    path = askdirectory()
    if len(path) > 0:
        get_files()
    return path


def get_files():
    global files, _width, _height
    files = os.listdir(path)
    msg = ''
    for line in files:
        msg += (line + '\n')
        _width = max(_width, len(line))

    msg = msg[:-1]
    _height = max(_height, len(files))
    text_before.config(state=NORMAL)
    text_new.config(state=NORMAL)
    text_before.delete(1.0, END)
    text_before.insert(END, msg)
    text_before.config(pady=10, padx=10, width=_width, height=_height, state=DISABLED)
    text_new.config(pady=10, padx=10, width=_width, height=_height, state=DISABLED)
    return files


def rename_files():
    global pattern, new_names, _width, _height
    new_title = entry_title.get()
    pattern = entry_pattern.get()
    new_pattern = entry_new_pattern.get()
    offset = int(entry_offset.get())
    i = 0
    for f in files:
        # Split file name from files extensions
        file_name, file_ext = os.path.splitext(f)

        # Detect where the pattern start is located
        index = file_name.find(pattern)

        if index != -1:
            if new_pattern == '':
                # Crop the file name from index to offset
                file_name = file_name[index:index + int(len(pattern)) + offset].upper()
            else:
                # Crop the file number
                file_name = file_name[index + int(len(pattern)):index + int(len(pattern)) + offset].upper()
                file_number = re.findall(r'\d+', file_name)
                file_name = new_pattern + str(file_number[0]).zfill(2)

            # Assign new Common title head and reassign extension
            new_name = new_title + file_name + file_ext
            new_names.insert(files.index(f), new_name)
        i = i + 1
    msg = ''
    for line in new_names:
        msg += (line + '\n')
        _width = max(_width, len(line))

    msg = msg[:-1]
    _height = max(_height, len(files))
    text_before.config(state=NORMAL)
    text_new.config(state=NORMAL)
    text_new.delete(1.0, END)
    text_new.insert(END, msg)
    text_before.config(pady=10, padx=10, width=_width, height=_height, state=DISABLED)
    text_new.config(pady=10, padx=10, width=_width, height=_height, state=DISABLED)
    return new_names


def save_changes():
    i = 0
    for f in files:
        if f.find(pattern) != -1:
            # Rename the file
            os.rename(path + '\\' + f, path + '\\' + new_names[i])
            i = i + 1


button_open = ttk.Button(root, text="Open", command=open_directory)
button_open.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=4)


def clear(e):
    global tmp
    if e.widget.get().endswith('...'):
        tmp = e.widget.get()
        e.widget.delete(0, END)


label_title = ttk.Label(root, text='Title')
label_title.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

entry_title = Entry(root)
entry_title.insert(0, 'Title ...')
entry_title.bind("<Button-1>", clear)
entry_title.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

label_pattern = ttk.Label(root, text='Pattern')
label_pattern.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

entry_pattern = Entry(root)
entry_pattern.insert(0, 'Pattern ...')
entry_pattern.bind("<Button-1>", clear)
entry_pattern.grid(row=1, column=3, sticky="nsew", padx=5, pady=5)

label_offset = ttk.Label(root, text='Offset')
label_offset.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

entry_offset = Entry(root)
entry_offset.insert(0, 'Offset ...')
entry_offset.bind("<Button-1>", clear)
entry_offset.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

label_new_pattern = ttk.Label(root, text='New Pattern')
label_new_pattern.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

entry_new_pattern = Entry(root)
entry_new_pattern.insert(0, 'New Pattern ...')
entry_new_pattern.bind("<Button-1>", clear)
entry_new_pattern.grid(row=2, column=3, sticky="nsew", padx=5, pady=5)

label_before = ttk.Label(root, text='Name')
label_before.grid(row=3, column=0, sticky="nsew", padx=5, pady=1, columnspan=2)

text_before = Text(root, height=1, width=20)
text_before.grid(row=4, column=0, sticky="nw", padx=5, pady=1, columnspan=2)
text_before.config(state=DISABLED)

label_New = ttk.Label(root, text='Name')
label_New.grid(row=3, column=2, sticky="nsew", padx=5, pady=1, columnspan=2)

text_new = Text(root, height=1, width=20)
text_new.grid(row=4, column=2, sticky="nw", padx=5, pady=1, columnspan=2)
text_new.config(state=DISABLED)

button_rename = ttk.Button(root, text="Rename", command=rename_files)
button_rename.grid(row=5, column=0, sticky="ns", padx=5, pady=5, columnspan=2)

button_save = ttk.Button(root, text="Save", command=save_changes)
button_save.grid(row=5, column=2, sticky="ns", padx=5, pady=5, columnspan=2)

# Menu Bar
menu = Menu(root)
root.config(menu=menu)

file = Menu(menu)

file.add_command(label='Open', command=open_directory)
file.add_command(label='Save', command=save_changes)
file.add_command(label='Exit', command=lambda: sys.exit())

menu.add_cascade(label='File', menu=file)
root.mainloop()
