import os
from queue import Queue
from threading import Thread
from tkinter import Tk
from tkinter import ttk

import cv2
import numpy as np
import pyautogui
import win32com.client as wincl
from PIL import Image
from PIL import ImageTk


# import pyttsx3
# import profile


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class EyeTracker:
    def __init__(self, q):
        self.start = False
        self.q = q
        self.directions = [0, 'Top', 0,
                           'Left', 'Center', 'Right',
                           0, 'Bottom', 0,
                           'Press Space']
        self.direction = [0] * 10
        self.eyeCascade = cv2.CascadeClassifier(resource_path("haarcascade_eye.xml"))
        self.faceCascade = cv2.CascadeClassifier(resource_path("haarcascade_frontalface_default.xml"))

        self.max_width = 0
        self.max_height = 0
        self.thresh = 0
        self.set_center = True
        self.eye_imgs = {'left': [], 'right': []}
        self.eyes_frame = None
        self.clicks = 0
        self.video_capture = cv2.VideoCapture(1)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.face_dim = (0, 0)
        self.offset_left = 5
        self.offset_right = 10
        self.divs = (24, 3)
        self.centered_img = []
        self.fixed_eye = False
        self.center_face = []
        self.center_eye = []
        self.center_retina = []

    def main(self):
        if self.start:
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)

            gray = self.detect_faces_eyes(frame)

            if len(self.center_face) > 0 and len(self.center_eye) > 0:
                self.detect_eye_move(gray)
                self.face_dim = self.center_face[0][1], self.center_face[0][2]

                data = {
                    'Direction': self.direction.index(max(self.direction)),
                    'Clicks': self.clicks,
                }
                self.q.put(data)

            frame = self.draw(frame)

            self.direction.clear()
            self.direction = [0] * 10

            self.control_input()

            return frame

    def draw(self, img):
        if len(self.center_face) > 0:
            rectangle = cv2.rectangle
            for face in self.center_face:
                rectangle(img,
                          (face[0][0] - face[1] // 2, face[0][1] - face[2] // 2),
                          (face[0][0] + face[1] // 2, face[0][1] + face[2] // 2),
                          (0, 0, 0), 2)

            for eye in self.center_eye:
                rectangle(img,
                          (eye[0][0] - eye[1] // 2, eye[0][1] - eye[2] // 2),
                          (eye[0][0] + eye[1] // 2, eye[0][1] + eye[2] // 2),
                          (0, 0, 255), 2)

            line = cv2.line
            for retina in self.center_retina:
                line(img, (retina[0] - 10, retina[1]),
                     (retina[0] + 10, retina[1]), (255, 0, 0), 2)
                line(img, (retina[0], retina[1] - 10),
                     (retina[0], retina[1] + 10), (255, 0, 0), 2)

        img = cv2.resize(img, (0, 0), fx=0.66, fy=0.66)
        if self.eyes_frame is not None:
            img = self.vcat(self.eyes_frame, img)

        return img

    def control_input(self):
        if not self.fixed_eye and len(self.center_retina) > 0:
            detected = False

            for center_retina in self.center_retina:
                for center in self.center_eye:
                    detected |= center[0][0] - center[1] // 2 < center_retina[0] < center[0][0] + center[1] // 2 and \
                                center[0][1] - center[2] // 2 < center_retina[1] < center[0][1] + center[2] // 2

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
        self.thresh = 0
        self.face_dim = (0, 0)
        self.center_eye.clear()

    def detect_faces_eyes(self, image):
        self.center_retina.clear()
        self.center_face.clear()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        br_level = int(cv2.mean(image)[0])
        if br_level < 128:
            cv2.equalizeHist(image, image)

        faces = self.faceCascade.detectMultiScale(
            image,
            scaleFactor=1.5,
            minNeighbors=5,
            minSize=(int(self.face_dim[0] * 0.8), int(self.face_dim[1] * 0.8)),
            maxSize=(int(self.face_dim[0] * 1.2), int(self.face_dim[1] * 1.2))
        )

        for (x, y, w, h) in faces:
            center_face = (x + w // 2, y + h // 2)
            roi = image[y:y + h, x:x + w]
            self.center_face.append((center_face, w, h))
            self.detect_eyes(roi, x, y, w, h)
        return image

    def detect_eyes(self, roi_gray, x, y, w, h):
        left_open = 0
        right_open = 0

        br_level = int(cv2.mean(roi_gray)[0])
        if br_level < 128:
            cv2.equalizeHist(roi_gray, roi_gray)

        eyes = self.eyeCascade.detectMultiScale(roi_gray,
                                                scaleFactor=1.5,
                                                minNeighbors=5,
                                                maxSize=(w // 2, h // 4),
                                                minSize=(w // 4, h // 4))
        for (ex, ey, ew, eh) in eyes:
            center_retina = (x + ex + ew // 2, y + ey + eh // 2)

            if y < center_retina[1] < y + h // 2:
                if self.set_center and len(self.center_eye) <= 2:
                    self.center_eye.append((center_retina, ew, eh))

                self.center_retina.append(center_retina)
                left_eye = center_retina[0] < x + w // 2

                if left_eye:
                    left_open = 1
                else:
                    right_open = 2

        self.clicks = left_open + right_open

    def detect_eye_move(self, src):
        img = np.zeros([128, 256])
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, 'Press Space Bar', (32, 64), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if len(self.center_eye) > 0:
            middle = src.shape[1] // 2
            for center in self.center_eye:
                img = src[center[0][1] - center[2] // 2:center[0][1] + center[2] // 2,
                      center[0][0] - center[1] // 2:center[0][0] + center[1] // 2]

                for face in self.center_face:
                    if face[0][0] - face[1] < center[0][0] < face[0][0] + face[1]:
                        middle = face[0][0]
                left_eye = center[0][0] < middle
                self.map_image(img, left_eye)

            img = self.hcat([self.eye_imgs['left'], self.eye_imgs['right']])
            self.eye_imgs['left'].clear()
            self.eye_imgs['right'].clear()

        self.eyes_frame = img

    def map_image(self, src, left):
        if self.set_center:
            self.offset_right = 0
            self.offset_left = 0

        divs = self.divs
        img_gray_enhanced = src.copy()
        h = img_gray_enhanced.shape[0]
        w = img_gray_enhanced.shape[1]

        offset = self.offset_left if left else self.offset_right

        if offset > 0:
            img_gray_enhanced[:, :w - offset] = img_gray_enhanced[:, offset:]
            img_gray_enhanced[:, w - offset:] = 255
        else:
            img_gray_enhanced[:, -offset:] = img_gray_enhanced[:, : w + offset]
            img_gray_enhanced[:, 0: -offset] = 255

        br_level = int(cv2.mean(img_gray_enhanced)[0])
        if br_level < 128:
            cv2.equalizeHist(img_gray_enhanced, img_gray_enhanced)

        side = 'left' if left else 'right'

        if len(self.eye_imgs[side]) == 0:
            img_mapped_black = cv2.resize(img_gray_enhanced, (divs[0], divs[0]), interpolation=cv2.INTER_AREA)
            self.limit_bounds(img_mapped_black, h, w)
            thresh = np.min(img_mapped_black)
            img_mapped_black = cv2.threshold(img_mapped_black, thresh, 255, cv2.THRESH_BINARY)[1]
            self.get_draw_center(img_mapped_black, img_mapped_black, radius=3)

            img_mapped_direction = cv2.resize(img_mapped_black, (divs[1], divs[1]), interpolation=cv2.INTER_AREA)
            thresh = np.min(img_mapped_direction)
            img_mapped_direction = cv2.threshold(img_mapped_direction, thresh, 255, cv2.THRESH_BINARY)[1]

            d = img_mapped_direction.argmin()
            if d != 0:
                if len(self.center_retina) == 0:
                    self.direction[7] += 1
                else:
                    self.direction[d] += 1

            img_mapped_black = cv2.resize(img_mapped_black, (h, w), interpolation=cv2.INTER_AREA)
            img_mapped_direction = cv2.resize(img_mapped_direction, (h, w), interpolation=cv2.INTER_AREA)
            # image_direction = self.divide_image(img_mapped_black, div=divs[1], return_image=True)
            center = self.get_draw_center(img_mapped_black, img_gray_enhanced, color=255)
            self.eye_imgs[side].append(img_gray_enhanced)
            self.eye_imgs[side].append(img_mapped_black)
            self.eye_imgs[side].append(img_mapped_direction)

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
                if len(self.center_retina) == 0:
                    self.direction[7] += 1
                else:
                    self.direction[d] += 1
            return f_image

    @staticmethod
    def hcat(img_list1, padding=10, scale=2):
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

        final_image = cv2.resize(final_image, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        return final_image

    @staticmethod
    def get_draw_center(src, dst, radius=5, color=0):
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
            return center

    @staticmethod
    def limit_bounds(img_mapped_black, h, w):
        img_mapped_black[:int(h * 0.1), :] = 255
        img_mapped_black[int(h * 0.9):, :] = 255
        img_mapped_black[:, :int(w * 0.1)] = 255
        img_mapped_black[:, int(w * 0.9):] = 255

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
        print('Eye Tracker')
        self.video_capture.release()
        self.q.put(False)


class MouseAndSpeech:
    def __init__(self, q, engine, m_pyautogui, move=True, talk=True, hor_div=16, ver_div=9):
        self.q = q
        self.talk = talk
        self.move = move
        self.m_pyautogui = m_pyautogui
        # self.engine = engine
        self.speak = engine
        self.max_samples = 5
        self.n_samples = 0

        self.directions = [0, 'Up', 0,
                           'Left', 'Center', 'Right',
                           0, 'Down', 0,
                           'Scanning ...']
        self.direction_samples = [0] * 9
        self.result_direction = 0

        w, h = self.m_pyautogui.size()
        x_offset = w // hor_div
        y_offset = h // ver_div
        self.duration = 0.2
        self.m_pyautogui.FAIL_SAFE = True
        self.m_pyautogui.PAUSE = self.duration
        self.m_pyautogui.moveTo(x=w // 2, y=h // 2, duration=self.duration)

        self.mouse_directions = [0,
                                 (0, -y_offset), 0,
                                 (-x_offset, 0), 0,
                                 (x_offset, 0), 0,
                                 (0, y_offset), 0, 0]
        self.click_samples = [0] * 4
        self.b_duration = 0.1
        self.result_click = 0

    def process(self):
        while True:
            data = self.q.get()
            self.q.task_done()
            if not data:
                break

            if self.n_samples <= self.max_samples:
                self.n_samples += 1
                self.direction_samples[data['Direction']] += 1
                self.click_samples[data['Clicks']] += 1
            else:
                self.n_samples = 0
                click = self.click_samples.index(max(self.click_samples))
                if click == 2 and self.click_samples[click] > self.max_samples * 0.9:
                    click = 4

                direction = self.direction_samples.index(max(self.direction_samples))

                if self.result_click != click:
                    self.handle_click(click)
                elif self.result_direction != direction:
                    self.handle_movement(direction)

                self.reset()

                # if self.talk:
                #     self.engine.runAndWait()
                # else:
                #     self.engine.stop()

    def handle_click(self, click):
        if self.result_click == 4 and click == 2 or self.result_click == 2 and click == 4:
            return
        self.result_click = click
        if self.result_click != 3:
            if click == 4:
                if self.talk: self.speak.Speak('Double Click')
                # self.engine.say('Double Click')
                if self.move:
                    self.m_pyautogui.click(clicks=2, duration=self.b_duration)
            elif click == 2:
                # self.engine.say('Left Click')
                if self.talk: self.speak.Speak('Left Click')
                if self.move:
                    self.m_pyautogui.click(button='left', duration=self.b_duration)
            elif click == 1:
                # self.engine.say('Right Click')
                if self.talk: self.speak.Speak('Right Click')
                if self.move:
                    self.m_pyautogui.click(button='right', duration=self.b_duration)

    def handle_movement(self, direction):
        self.result_direction = direction
        if self.result_direction not in [0, 2, 4, 6, 8]:
            # self.engine.say(str(self.directions[direction]))
            if self.talk: self.speak.Speak(str(self.directions[direction]))
            if self.move:
                self.m_pyautogui.moveRel(xOffset=self.mouse_directions[direction][0],
                                         yOffset=self.mouse_directions[direction][1], duration=self.duration)

    def reset(self):
        self.n_samples = 0
        self.click_samples = [0] * 4
        self.direction_samples = [0] * 9

    def __del__(self):
        print('Mouse And Speech')


class EyeTrackerTkinter:
    def __init__(self):
        q = Queue()
        speak = wincl.Dispatch("SAPI.SpVoice")
        speak.Volume = 100
        mouse = MouseAndSpeech(q, speak, pyautogui, move=False, talk=True, hor_div=20, ver_div=30)
        t = Thread(target=mouse.process)
        t.start()

        self.q = q
        self.t = t
        self.eye_tracker = EyeTracker(q)
        self.frame = None
        self.draw = False
        self.fps = 15

        self.root = Tk()
        self.root.iconbitmap(default=resource_path('icon.ico'))
        self.root.title("Eye Tracker Tkinter")
        self.panel = None
        self.button_start = ttk.Button(self.root, text="Start", command=self.toggle_draw)
        self.button_start.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, columnspan=2)

        self.button_scan = ttk.Button(self.root, text="Scan", command=self.eye_tracker.scan)
        self.button_scan.grid(row=0, column=2, sticky="nsew", padx=10, pady=10, columnspan=2)

        self.videoLoop()

    def videoLoop(self):
        if self.draw:
            image = self.eye_tracker.main()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            if self.panel is None:
                self.panel = ttk.Label(image=image)
                self.panel.image = image
                self.panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10, columnspan=4)
            else:
                self.panel.configure(image=image)
                self.panel.image = image

        self.root.after(1000 // self.fps, self.videoLoop)

    def toggle_draw(self):
        self.draw ^= 1
        self.eye_tracker.start ^= 1

    def __del__(self):
        print('Tkinter')
        self.q.put(False)
        self.q.join()
        self.t.join()
        self.root.quit()


def main():
    eye_tracker_tkinter = EyeTrackerTkinter()
    eye_tracker_tkinter.root.mainloop()


if __name__ == '__main__':
    # profile.run('main()', sort=2)
    main()
