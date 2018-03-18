import os
import sys
from queue import LifoQueue
from threading import Thread
from tkinter import Tk, ttk, BooleanVar, IntVar, StringVar, Frame, Menu, messagebox

import cv2
import numpy as np
import pyautogui
import pyttsx3
import serial
from PIL import Image
from PIL import ImageTk

LARGE_FONT = ("Pulsa", 12)


class MyApp(Tk):
    __title__ = "Senior"

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self)
        container.grid()

        self.serial = SerialComm()

        self.frames = {}
        self.q = LifoQueue()
        self.eye_tracker = EyeTracker(self.q)

        self.variables = {}

        self.fps = IntVar()
        self.fps.set(20)

        self.temp = IntVar()
        self.temp.set(20)
        self.temp.trace("w", self.send_command)
        self.variables[self.temp.__str__()] = 't', self.temp

        self.temp_current = StringVar()
        self.temp_current.set('Temperature')

        self.temp_offset = IntVar()
        self.temp_offset.set(5)
        self.temp_offset.trace("w", self.send_command)
        self.variables[self.temp_offset.__str__()] = 'o', self.temp_offset

        self.samples = 9

        self.window = IntVar()
        self.window.trace("w", self.send_command)
        self.variables[self.window.__str__()] = 'w', self.window

        self.talk = BooleanVar()
        self.talk.set(True)
        self.talk.trace("w", self.send_command)

        self.alarm = BooleanVar()
        self.alarm.set(False)
        self.alarm.trace("w", self.send_command)
        self.variables[self.alarm.__str__()] = 'a', self.alarm

        self.light = BooleanVar()
        self.light.set(False)
        self.light.trace("w", self.send_command)
        self.variables[self.light.__str__()] = 'l', self.light

        self.heater = BooleanVar()
        self.heater.set(False)
        self.heater.trace("w", self.send_command)
        self.variables[self.heater.__str__()] = 'h', self.heater

        self.ac = BooleanVar()
        self.ac.set(False)
        self.ac.trace("w", self.send_command)
        self.variables[self.ac.__str__()] = 'f', self.ac

        self.move = BooleanVar()
        self.move.set(False)

        self.hor_div = IntVar()
        self.hor_div.set(20)

        self.ver_div = IntVar()
        self.ver_div.set(30)

        self.mouse = MouseAndSpeech(self)
        self.t = Thread(target=self.mouse.process)
        self.t.start()

        self.frame = None
        self.draw = False

        frame = Preview(container, self)
        self.frames[Preview] = frame
        frame.grid(row=0, column=1, sticky="nsew", rowspan=100)
        self.current_frame = frame

        frame = Settings(container, self)
        self.frames[Settings] = frame
        frame.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)
        frame.grid_remove()

        frame = Applications(container, self)
        self.frames[Applications] = frame
        frame.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)
        frame.grid_remove()

        # Menu Bar
        menu = MyMenu(self)
        self.config(menu=menu)

        Tk.iconbitmap(self, default='icon.ico')
        Tk.wm_title(self, "Senior")
        w = (self.winfo_screenwidth() - self.eye_tracker.window_size) // 2
        self.geometry('+{}+{}'.format(w, 0))
        self.protocol("WM_DELETE_WINDOW", lambda: self.close())

    def show_frame(self, cont):
        if self.current_frame is not None:
            self.current_frame.grid_remove()
        frame = self.frames[cont]
        frame.grid()
        self.current_frame = frame

    def send_command(self, widget, *args):
        w = self.variables[widget]
        try:
            indicator = w[0]
            value = str(int(w[1].get()))
            if indicator == 'f' and value == '1':
                self.heater.set(False)
                self.serial.send_serial('h0')
            elif indicator == 'h' and value == '1':
                self.ac.set(False)
                self.serial.send_serial('f0')
            elif indicator == 't':
                self.heater.set(False)
                self.ac.set(False)

            s = indicator + value
            self.serial.send_serial(s)
        except:
            pass

    def close(self):
        print(self.__title__)
        self.eye_tracker.video_capture.release()
        if self.mouse.isTalking:
            self.destroy()
        clear_queue(self.q)
        self.q.put(False)
        self.q.join()
        self.t.join()
        self.destroy()


class MyMenu(Menu):
    def __init__(self, parent):
        Menu.__init__(self)

        apps = Menu(self)
        apps.add_command(label=parent.frames[Preview].__title__,
                         command=lambda: parent.show_frame(Preview))
        apps.add_command(label=parent.frames[Settings].__title__,
                         command=lambda: parent.show_frame(Settings))
        apps.add_command(label=parent.frames[Applications].__title__,
                         command=lambda: parent.show_frame(Applications))
        apps.add_command(label='Exit', command=lambda: parent.close())
        self.add_cascade(label='View', menu=apps)

        info = Menu(self)
        info.add_command(label='Help', command=lambda: print('Help'))
        info.add_command(label='About',
                         command=lambda: messagebox.showinfo('About', 'About us text \netc \netc \netc'))
        self.add_cascade(label='Help', menu=info)


class Preview(Frame):
    __title__ = 'Preview'

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.button_scan = ttk.Button(self, text="Calibrate", command=self.controller.eye_tracker.scan)
        self.button_start = ttk.Button(self, text="Start", command=self.toggle_draw)
        self.panel_video = ttk.Label(self)

        self.button_start.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.button_scan.grid(row=0, column=1, sticky="new", padx=10, pady=10)
        self.panel_video.grid(row=1, column=0, sticky="new", padx=10, pady=10, columnspan=2)

        self.videoLoop()

    def videoLoop(self):
        if self.controller.draw:
            image = self.controller.eye_tracker.main()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            self.panel_video.configure(image=image)
            self.panel_video.image = image

        self.controller.temp_current.set('Temperature: ' + self.controller.serial.read_serial().strip() + '°C')

        try:
            fps = self.controller.fps.get()
            if 10 > fps > 50:
                fps = 50
            self.after(1000 // fps, self.videoLoop)
        except:
            self.after(1000 // 10, self.videoLoop)

    def toggle_draw(self):
        if self.controller.eye_tracker.started is None:
            self.controller.show_frame(Preview)
        self.controller.draw ^= 1
        self.controller.eye_tracker.start ^= 1
        self.button_start.config(text="Pause" if self.controller.draw else "Resume")

    def __del__(self):
        print(self.__title__)


class Settings(Frame):
    __title__ = 'Settings'

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, width=768, height=576)
        self.controller = controller

        self.button_move = ttk.Checkbutton(self, text="Move Mouse", command=self.toggle_speak_move,
                                           var=self.controller.move)
        self.button_speak = ttk.Checkbutton(self, text="Audio", command=self.toggle_speak_move,
                                            var=self.controller.talk)
        self.frame_fps = ttk.Frame(self)
        self.panel = ttk.Label(self.frame_fps, text='FPS')
        self.panel.pack(anchor='nw')
        self.entry_fps = ttk.Entry(self.frame_fps, textvariable=self.controller.fps)
        self.entry_fps.pack(anchor='nw')

        self.frame_hor_div = ttk.Frame(self)
        self.panel = ttk.Label(self.frame_hor_div, text='Horizontal Division')
        self.panel.pack(anchor='nw')
        self.entry_hor_div = ttk.Entry(self.frame_hor_div, textvariable=self.controller.hor_div)
        self.entry_hor_div.pack(anchor='nw')

        self.frame_ver_div = ttk.Frame(self)
        self.panel = ttk.Label(self.frame_ver_div, text='Vertical Division')
        self.panel.pack(anchor='w')
        self.entry_ver_div = ttk.Entry(self.frame_ver_div, textvariable=self.controller.ver_div)
        self.entry_ver_div.pack(anchor='w')

        self.frame_temp = ttk.Frame(self)
        self.panel = ttk.Label(self.frame_temp, text='Temperature Offset')
        self.panel.pack(anchor='nw')
        self.entry_temp_offset = ttk.Entry(self.frame_temp, textvariable=self.controller.temp_offset)
        self.entry_temp_offset.pack(anchor='nw')

        self.button_move.grid(row=2, column=0, sticky="new", padx=10, pady=10)
        self.button_speak.grid(row=3, column=0, sticky="new", padx=10, pady=10)
        self.frame_hor_div.grid(row=4, column=0, sticky="new", padx=10, pady=10)
        self.frame_ver_div.grid(row=5, column=0, sticky="new", padx=10, pady=10)
        self.frame_fps.grid(row=6, column=0, sticky="new", padx=10, pady=10)
        self.frame_temp.grid(row=7, column=0, sticky="new", padx=10, pady=10)

    def toggle_speak_move(self):
        clear_queue(self.controller.q)
        self.controller.q.put((self.controller.talk.get(), self.controller.move.get()))

    def __del__(self):
        print(self.__title__)


class Applications(Frame):
    __title__ = 'Applications'

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, width=768, height=576)

        self.toggle_ac = None
        self.toggle_heater = None
        self.toggle_light = None
        self.toggle_alarm = None
        self.controller = controller

        self.button_alarm = ttk.Checkbutton(self, text="Alarm", var=self.controller.alarm)
        self.button_light = ttk.Checkbutton(self, text="Light", var=self.controller.light)
        self.button_heater = ttk.Checkbutton(self, text="Heater", var=self.controller.heater)
        self.button_ac = ttk.Checkbutton(self, text="AC", var=self.controller.ac)

        self.frame_temp = ttk.Frame(self)
        self.panel = ttk.Label(self.frame_temp, textvariable=self.controller.temp_current)
        self.panel.pack(anchor='w')
        self.entry_temp = ttk.Entry(self.frame_temp, textvariable=self.controller.temp)
        self.entry_temp.pack(anchor='w')

        self.frame_window = ttk.Frame(self)
        self.panel_window = ttk.Label(self.frame_window, text='Window')
        self.button_group_window0 = ttk.Radiobutton(self.frame_window, text='0%',
                                                    variable=self.controller.window, value=0)
        self.button_group_window25 = ttk.Radiobutton(self.frame_window, text='25%',
                                                     variable=self.controller.window, value=25)
        self.button_group_window50 = ttk.Radiobutton(self.frame_window, text='50%',
                                                     variable=self.controller.window, value=50)
        self.button_group_window100 = ttk.Radiobutton(self.frame_window, text='100%',
                                                      variable=self.controller.window, value=100)
        self.panel_window.pack(anchor='w')
        self.button_group_window0.pack(side='left')
        self.button_group_window25.pack(side='left')
        self.button_group_window50.pack(side='left')
        self.button_group_window100.pack(side='left')

        self.button_alarm.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.button_light.grid(row=0, column=1, sticky="new", padx=10, pady=10)
        self.button_heater.grid(row=0, column=2, sticky="new", padx=10, pady=10)
        self.button_ac.grid(row=0, column=3, sticky="new", padx=10, pady=10)
        self.frame_temp.grid(row=0, column=4, sticky="new", padx=10, pady=10)
        self.frame_window.grid(row=0, column=5, sticky="new", padx=10, pady=10)

        self.button_alarm.focus()

    def __del__(self):
        print(self.__title__)


class EyeTracker:
    __title__ = 'Eye Tracker'

    def __init__(self, q):
        self.started = None
        self.start = False
        self.q = q
        self.directions = [0, 'Top', 0,
                           'Left', 'Center', 'Right',
                           0, 'Bottom', 0,
                           'Press Space']
        self.direction = [0] * 10
        self.eyeCascade = cv2.CascadeClassifier(resource_path("haarcascade_eye.xml"))
        self.faceCascade = cv2.CascadeClassifier(resource_path("haarcascade_frontalface_default.xml"))

        self.scale = 0.25
        self.max_width = 0
        self.max_height = 0
        self.thresh = 0
        self.set_center = True
        self.eye_imgs = [[], []]
        self.eyes_frame = None
        self.clicks = 0
        self.video_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.fram_ratio = self.frame_width // self.frame_height
        self.padding = 10
        self.window_size = int(self.frame_width * self.scale + 2 * self.padding)
        self.face_dim = (0, 0)
        self.offset_left = 5
        self.offset_right = 10
        self.divs = (24, 3)
        self.centered_img = []
        self.fixed_eye = False
        self.center_face = None
        self.center_eye = [None] * 2
        self.center_retina = [None] * 2
        self.mouse = [[None] * 3] * 2

    def main(self):
        if self.start:
            if self.start != self.started:
                self.started = self.start
                self.scan()

            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)

            gray = self.detect_faces_eyes(frame)
            if self.center_face is not None \
                    and self.center_eye[0] is not None \
                    and self.center_eye[1] is not None:
                self.detect_eye_move(gray)
                self.face_dim = self.center_face[1], self.center_face[2]

                data = {
                    'Direction': self.direction.index(max(self.direction)),
                    'Clicks': self.clicks,
                    'Mouse': self.mouse,
                }
                self.q.put(data)

            frame = self.draw(frame)

            self.direction = [0] * 10
            self.mouse = [[None] * 3] * 2
            self.control_input()

            return frame

    def detect_faces_eyes(self, image):
        self.center_face = None

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        br_level = int(cv2.mean(image)[0])
        if br_level < 128:
            cv2.equalizeHist(image, image)

        faces = self.faceCascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(int(self.face_dim[0] * 0.8), int(self.face_dim[1] * 0.8)),
            maxSize=(int(self.face_dim[0] * 1.2), int(self.face_dim[1] * 1.2))
        )

        for (x, y, w, h) in faces:
            center_face = (x + w // 2, y + h // 2)
            roi = image[y:y + h, x:x + w]
            self.center_face = (center_face, w, h)
            self.detect_eyes(roi, x, y, w, h)
            break
        return image

    def detect_eyes(self, roi_gray, x, y, w, h):
        self.center_retina = [None] * 2

        left_open = 0
        right_open = 0

        br_level = int(cv2.mean(roi_gray)[0])
        if br_level < 128:
            cv2.equalizeHist(roi_gray, roi_gray)

        eyes = self.eyeCascade.detectMultiScale(roi_gray,
                                                scaleFactor=1.1,
                                                minNeighbors=5,
                                                maxSize=(w // 2, h // 4),
                                                minSize=(w // 8, h // 8))
        for (ex, ey, ew, eh) in eyes:
            center_retina = (x + ex + ew // 2, y + ey + eh // 2)

            if y < center_retina[1] < y + h // 2:  # Eyes can't be below half of face.
                left_eye = center_retina[0] < x + w // 2
                side = 0 if left_eye else 1

                if self.set_center and self.center_eye[side] is None:
                    self.center_eye[side] = (center_retina, ew, eh)

                self.center_retina[side] = center_retina

                if left_eye:
                    left_open = 1
                else:
                    right_open = 2

        self.clicks = left_open + right_open

    def detect_eye_move(self, src):
        middle = src.shape[1] // 2
        for center in self.center_eye:
            (x, y), w, h = center
            img = src[y - h // 2:y + h // 2,
                  x - w // 2:x + w // 2]

            (f_x, f_y), f_w, f_h = self.center_face
            if f_x - f_w < x < f_x + f_w:
                middle = f_x
            left_eye = x < middle
            self.get_pupil(img, left_eye)

        img = self.hcat([self.eye_imgs[0], self.eye_imgs[1]], self.window_size)
        self.eye_imgs[0].clear()
        self.eye_imgs[1].clear()

        self.eyes_frame = img

    def get_pupil(self, src, left):
        h, w = src.shape

        # Shift image according to the offset saved when calibrating.
        self.centralize_eye(src, left)

        # If image too dark, improve Contrast.
        br_level = int(cv2.mean(src)[0])
        if br_level < 128:
            cv2.equalizeHist(src, src)

        side = 0 if left else 1
        if len(self.eye_imgs[side]) == 0:
            # Crop Image, to avoid eyebrows and corner of the eye.
            img_mapped_black = src.copy()
            self.limit_bounds(img_mapped_black, h, w)

            # Get Threshold and turn image into Black and White.
            thresh = np.min(img_mapped_black) + 0.1 * np.mean(img_mapped_black)
            img_mapped_black = cv2.threshold(img_mapped_black, int(thresh), 255, cv2.THRESH_BINARY)[1]

            # Draw a Circle at the center of the original image (For Debug)
            center = self.get_draw_center(img_mapped_black, src, color=255)

            # Attempt to control mouse directly 'Go where i Look'.
            self.mouse[side] = center, self.center_eye[side][1], self.center_eye[side][2]

            # Resize image into 3x3.
            img_mapped_direction = cv2.resize(img_mapped_black, (3, 3), interpolation=cv2.INTER_AREA)

            # Get Threshold and turn image into Black and White.
            thresh = np.min(img_mapped_direction)
            img_mapped_direction = cv2.threshold(img_mapped_direction, thresh, 255, cv2.THRESH_BINARY)[1]

            # Fill center if eye is blinking. Left (click == 2, side = 0) Right (click == 1, side == 1)
            if self.clicks + side == 2:
                img_mapped_direction[:, :] = 255
                img_mapped_direction[1, 1] = 0
            # Both Eyes Closed, signal for Down.
            elif self.clicks == 0:
                img_mapped_direction[:, :] = 255
                img_mapped_direction[2, 1] = 0

            # Set Direction as Location of darkest pixel
            d = img_mapped_direction.argmin()
            self.direction[d] += 1

            # Resize to Original Size.
            img_mapped_direction = cv2.resize(img_mapped_direction, (h, w), interpolation=cv2.INTER_AREA)

            # Save Images to display.
            self.eye_imgs[side].append(src)
            self.eye_imgs[side].append(img_mapped_black)
            self.eye_imgs[side].append(img_mapped_direction)

            # When calibrating calculate how far the retina is from the center of the image.
            if self.set_center:
                offset = center[0] - w // 2
                if left:
                    self.offset_left = offset
                else:
                    self.offset_right = offset

    def divide_image(self, img, div, return_image=False):
        h = img.shape[0]
        w = img.shape[1]
        index = 0
        d = 0
        br_max = 255

        for y in range(div):
            for x in range(div):
                i = img[y * h // div:(y + 1) * h // div,
                    x * w // div: (x + 1) * w // div]
                i = i.copy()
                br = cv2.mean(i)
                if not return_image:
                    i.fill(255)

                if br[0] < br_max:
                    br_max = br[0]
                    self.thresh = br_max

        if return_image:
            f_image = np.zeros([h, w])
            for y in range(div):
                for x in range(div):
                    i = img[y * h // div:(y + 1) * h // div,
                        x * w // div: (x + 1) * w // div]
                    i = i.copy()
                    br = cv2.mean(i)
                    if h * 0.3 < y < h * 0.7 or w * 0.3 < x < w * 0.7:
                        i.fill(br[0])
                    else:
                        i.fill(255)

                    if br[0] <= br_max and index in [1, 3, 4, 5, 7]:
                        i.fill(0)
                        d = index
                    else:
                        i.fill(255)

                    index += 1
                    f_image[y * h // div:(y + 1) * h // div, x * w // div: (x + 1) * w // div] = i.copy()

            if d != 0:
                if self.center_retina[0] is None:
                    self.direction[7] += 1
                else:
                    self.direction[d] += 1
            return f_image

    def draw(self, img):
        if self.center_face is not None:
            rectangle = cv2.rectangle
            (f_x, f_y), f_w, f_h = self.center_face
            rectangle(img,
                      (f_x - f_w // 2, f_y - f_h // 2),
                      (f_x + f_w // 2, f_y + f_h // 2),
                      (0, 0, 0), 2)

            if self.center_eye[0] is not None and self.center_eye[1] is not None:
                for eye in self.center_eye:
                    (e_x, e_y), e_w, e_h = eye
                    rectangle(img,
                              (e_x - e_w // 2, e_y - e_h // 2),
                              (e_x + e_w // 2, e_y + e_h // 2),
                              (0, 0, 255), 2)

            line = cv2.line
            for retina in self.center_retina:
                if retina is not None:
                    r_x, r_y = retina
                    line(img, (r_x - 10, r_y), (r_x + 10, r_y), (255, 0, 0), 2)
                    line(img, (r_x, r_y - 10), (r_x, r_y + 10), (255, 0, 0), 2)

        img = cv2.resize(img, (0, 0), fx=self.scale, fy=self.scale)
        if self.eyes_frame is not None:
            img = self.vcat(self.eyes_frame, img)

        return img

    def control_input(self):
        if not self.fixed_eye and self.center_retina[0] is not None and self.center_retina[1] is not None:
            detected = False

            for center_retina in self.center_retina:
                for center in self.center_eye:
                    if center is not None:
                        (x, y), w, h = center
                        detected |= x - w // 2 < center_retina[0] < x + w // 2 and \
                                    y - h // 2 < center_retina[1] < y + h // 2

            if not detected:
                self.direction[9] = -1

        if self.direction[9] == -1:
            self.scan()
            return True
        else:
            self.set_center = False
            return True

    def scan(self):
        self.set_center = True
        self.offset_right = 0
        self.offset_left = 0
        self.thresh = 0
        self.face_dim = (0, 0)
        self.center_eye = [None] * 2

    def centralize_eye(self, src, left):
        h, w = src.shape
        offset = self.offset_left if left else self.offset_right
        if offset > 0:
            src[:, :w - offset] = src[:, offset:]
            src[:, w - offset:] = 255
        else:
            src[:, -offset:] = src[:, : w + offset]
            src[:, 0: -offset] = 255

    @staticmethod
    def get_draw_center(src, dst, radius=5, color=0):
        try:
            radius = radius * src.shape[1] // 100
            output = cv2.connectedComponentsWithStats(src, connectivity=8, ltype=cv2.CV_32S)
            center = output[3][0]
            cv2.circle(dst, (int(center[0]), int(center[1])), radius, color, thickness=-1)
            return int(center[0]), int(center[1])
        except:
            x_list = []
            y_list = []
            for y in range(src.shape[0]):
                for x in range(src.shape[1]):
                    if src[y, x] == 0:  # and (src.shape[0]*0.3 < y < src.shape[0]*0.7 or
                        # src.shape[1]*0.3 < x < src.shape[1]*0.7):
                        x_list.append(x)
                        y_list.append(y)

            if len(x_list) > 0:
                center = (min(x_list) + (max(x_list) - min(x_list)) // 2,
                          min(y_list) + (max(y_list) - min(y_list)) // 2)

                cv2.circle(dst, center, radius, color, thickness=-1)
                # print('Except', center)
                return center

    @staticmethod
    def limit_bounds(img_mapped_black, h, w):
        img_mapped_black[:int(h * 0.1), :] = 255
        img_mapped_black[int(h * 0.9):, :] = 255
        img_mapped_black[:, :int(w * 0.1)] = 255
        img_mapped_black[:, int(w * 0.9):] = 255

    @staticmethod
    def hcat(img_list1, window_size, padding=10):
        max_width = []
        max_height = []
        n_images = 0
        img_height = 0
        img_width = 0
        current_x = 0
        current_y = 0

        for img_list in img_list1:
            for img in img_list:
                max_height.append(img.shape[0])
                max_width.append(img.shape[1])
                n_images = len(img_list)

        if np.size(max_height) > 0:
            img_height = np.max(max_height)
            img_width = np.max(max_width)

        final_image = np.zeros((img_height * 2 + padding, n_images * (img_width + padding) - padding, 3),
                               dtype=np.uint8)
        final_image[:, :, 0].fill(128)
        final_image[:, :, 1].fill(0)
        final_image[:, :, 2].fill(128)

        index = 0
        for img_list in img_list1:
            for image in img_list:
                index += 1
                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 0] = image

                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 1] = image

                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 2] = image

                current_x += image.shape[0] + padding

            current_y += img_height + padding
            current_x = 0

        img_list1.clear()
        h, w = final_image.shape[:2]
        h = (window_size * h) // w
        w = window_size

        final_image = cv2.resize(final_image, (w, h), interpolation=cv2.INTER_AREA)

        return final_image

    @staticmethod
    def vcat(eyes_frame, img):
        h1, w1 = img.shape[:2]
        h2, w2 = eyes_frame.shape[:2]

        w = max(w1, w2)
        vis = np.zeros((h1 + h2, w, 3), np.uint8)
        vis[:, :, 0].fill(128)
        vis[:, :, 1].fill(0)
        vis[:, :, 2].fill(128)

        vis[:h2, (-w2 // 2) + w // 2:(+w2 // 2) + w // 2] = eyes_frame
        vis[h2:, (-w1 // 2) + w // 2:(+w1 // 2) + w // 2] = img

        return vis

    def __del__(self):
        print(self.__title__)


class MouseAndSpeech:
    __title__ = 'Mouse And Speech'

    def __init__(self, controller):
        self.controller = controller

        self.isTalking = False
        self.mouse = None
        self.q = self.controller.q
        self.m_talk = self.controller.talk.get()
        self.m_move = self.controller.move.get()
        self.hor_div = self.controller.hor_div
        self.m_hor_div = self.hor_div.get()

        self.ver_div = self.controller.ver_div
        self.m_ver_div = self.ver_div.get()

        self.m_pyautogui = pyautogui
        self.engine = pyttsx3.init()
        # self.engine.connect('started-utterance', self.onStart)
        # self.engine.connect('finished-utterance', self.onEnd)

        self.max_samples = self.controller.samples
        self.n_samples = 0

        self.directions = ['Top Left', 'Up', 'Top Right',
                           'Left', 'Center', 'Right',
                           'Bottom Left', 'Down', 'Bottom Right',
                           'Scanning ...']
        self.direction_samples = [0] * 9
        self.result_direction = 0

        self.w, self.h = self.m_pyautogui.size()
        self.x, self.y = self.w // 2, self.h // 2
        x_offset = self.w // self.m_hor_div
        y_offset = self.h // self.m_ver_div
        self.mouse_directions = [(-x_offset, -y_offset), (0, -y_offset), (x_offset, -y_offset),
                                 (-x_offset, 0), 0, (x_offset, 0),
                                 (-x_offset, y_offset), (0, y_offset), (x_offset, y_offset),
                                 0]
        self.duration = 0.2
        self.m_pyautogui.FAIL_SAFE = True
        self.m_pyautogui.PAUSE = self.duration

        self.click_samples = [0] * 4
        self.b_duration = 0.1
        self.result_click = 0

    def process(self):
        while True:
            data = self.q.get()
            self.q.task_done()

            if not data:
                break

            if isinstance(data, tuple):
                self.m_talk = data[0]
                self.m_move = data[1]
                if self.hor_div.get() != self.m_hor_div or self.ver_div.get() != self.m_ver_div:
                    self.m_hor_div = self.hor_div.get()
                    self.m_ver_div = self.ver_div.get()
                    x_offset = self.w // self.m_hor_div
                    y_offset = self.h // self.m_ver_div
                    self.mouse_directions = [0,
                                             (0, -y_offset), 0,
                                             (-x_offset, 0), 0,
                                             (x_offset, 0), 0,
                                             (0, y_offset), 0, 0]
            else:
                if self.n_samples <= self.max_samples:
                    self.n_samples += 1
                    self.direction_samples[data['Direction']] += 1
                    self.click_samples[data['Clicks']] += 1

                    # self.mouse = data['Mouse']
                    # center, w, h = self.mouse[1]
                    # x, y = self.lerp((center[0] / w, center[1] / h))
                    #
                    # self.m_pyautogui.moveTo(x=x * self.w*1.1,
                    #                         y=y * self.h*1.1, duration=0)
                    # print('x: {:.2} y: {:.2}'.format(x, y))

                else:
                    self.n_samples = 0
                    click = self.click_samples.index(max(self.click_samples))
                    if click == 2 and self.click_samples[click] > self.max_samples * 0.9:
                        click = 4

                    direction = self.direction_samples.index(max(self.direction_samples))

                    if self.result_click != click:
                        if self.m_talk:
                            self.handle_talk(False, click)
                        if self.m_move:
                            self.handle_click(click)

                    elif self.result_direction != direction:
                        if self.m_talk:
                            self.handle_talk(True, direction)
                        if self.m_move:
                            self.handle_movement(direction)

                    self.reset()

                    if self.m_talk:
                        self.engine.runAndWait()

            clear_queue(self.q)

    def handle_click(self, click):
        if self.result_click == 4 and click == 2 or self.result_click == 2 and click == 4:
            return
        self.result_click = click

        if self.controller.current_frame is self.controller.frames[Applications]:
            w = self.controller.focus_get()
            if click != 3:
                w.invoke()
        else:
            if self.result_click != 3:
                if click == 4:
                    self.m_pyautogui.click(clicks=2, duration=self.b_duration)
                elif click == 2:
                    self.m_pyautogui.click(button='left', duration=self.b_duration)
                elif click == 1:
                    self.m_pyautogui.click(button='right', duration=self.b_duration)

    def handle_movement(self, direction):
        if self.controller.current_frame is self.controller.frames[Applications]:
            w = self.controller.focus_get()

            if direction == 3:
                w.tk_focusPrev().focus()
            elif direction == 5:
                w.tk_focusNext().focus()
        else:
            self.result_direction = direction
            if self.result_direction != 4:
                self.m_pyautogui.moveRel(xOffset=self.mouse_directions[direction][0],
                                         yOffset=self.mouse_directions[direction][1], duration=self.duration)

    def handle_talk(self, movement, click):
        if movement:
            direction = click
            self.result_direction = direction
            if self.result_direction != 4:
                if self.m_talk: self.engine.say(str(self.directions[direction]))
        else:
            if self.result_click == 4 and click == 2 or self.result_click == 2 and click == 4:
                return
            self.result_click = click
            if self.result_click != 3:
                if click == 4:
                    self.engine.say('Double Click')
                elif click == 2:
                    self.engine.say('Left Click')
                elif click == 1:
                    self.engine.say('Right Click')

    def reset(self):
        self.n_samples = 0
        self.click_samples = [0] * 4
        self.direction_samples = [0] * 9

    def onStart(self, name):
        print('Started')
        self.isTalking = True

    def onEnd(self, name, completed):
        print('Ended')
        self.isTalking = False

    def lerp(self, center, per=0.5):
        x, y = center
        x = self.x + (x - self.x) * per
        y = self.y + (y - self.y) * per
        self.x = x
        self.y = y
        return x, y

    def __del__(self):
        print(self.__title__)


class SerialComm:
    def __init__(self):
        self.connected = False
        try:
            self.port = serial.Serial('COM5', baudrate=9600, timeout=1)
            self.connected = True
        except:
            pass

    def read_serial(self):
        res = ''
        try:
            res = self.port.readline().decode()
        finally:
            return res

    def send_serial(self, text):
        text += '#'
        self.port.write(text.encode())


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def clear_queue(q):
    """
        Clears all items from the queue.
    """
    with q.mutex:
        unfinished = q.unfinished_tasks - len(q.queue)
        if unfinished <= 0:
            if unfinished < 0:
                raise ValueError('task_done() called too many times')
        q.all_tasks_done.notify_all()
        q.unfinished_tasks = unfinished
        q.queue.clear()
        q.not_full.notify_all()


if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
