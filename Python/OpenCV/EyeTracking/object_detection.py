from queue import Queue
from threading import Thread

import cv2
import numpy as np
import pyttsx3


# import profile


class ObjectDetection:
    def __init__(self, q, draw_frame=True):
        self.direction = 0
        self.eyeCascade = cv2.CascadeClassifier("..\models\haarcascade_eye.xml")
        self.faceCascade = cv2.CascadeClassifier("..\models\haarcascade_frontalface_default.xml")

        self.q = q
        self.max_width = 0
        self.max_height = 0
        self.thresh = 0
        self.draw_frame = draw_frame
        self.set_center = False
        self.eye_imgs = {'left': [], 'right': []}
        self.eyes = None
        self.open_left = False
        self.open_right = False
        self.video_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.face_dim = (0, 0)
        self.fps = 20
        self.divs = (24, 3)
        self.fixed_eye = True
        self.center_face = []
        self.center_eye = []
        self.center_retina = []

    def main(self):
        while True:
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)

            self.detect_faces_eyes(frame)
            self.detect_eye_move(frame)

            if len(self.center_face) > 0 and len(self.center_eye) > 0:
                self.face_dim = self.center_face[0][1], self.center_face[0][2]

            if self.draw_frame:
                self.draw(frame)

            d = {
                'Direction': self.direction,
                'Left': self.open_left,
                'Right': self.open_right
            }

            self.q.put(d)
            stop = not self.control_input()

            if stop:
                self.q.put(False)
                break

    def draw(self, img):
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

        cv2.imshow('Video', img)
        cv2.namedWindow("Eyes", cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('Eyes', self.eyes.shape[1], self.eyes.shape[0])
        cv2.imshow('Eyes', self.eyes)

    def control_input(self):
        if not self.fixed_eye:
            detected = False

            for center_retina in self.center_retina:
                for center in self.center_eye:
                    detected |= center[0][0] - center[1] // 2 < center_retina[0] < center[0][0] + center[1] // 2 and \
                                center[0][1] - center[2] // 2 < center_retina[1] < center[0][1] + center[2] // 2

            if not detected:
                self.direction = 0

        key = cv2.waitKey(1000 // self.fps)

        if key in [ord('c'), 32] or self.direction == 0:
            self.scan()
            return True

        elif key in [ord('q'), ord('\x1b')] or (self.draw_frame and cv2.getWindowProperty('Video', 0) < 0):
            return False
        else:
            self.set_center = False
            return True

    def scan(self):
        self.set_center = True
        self.thresh = 0
        self.center_eye.clear()

    def detect_faces_eyes(self, image):
        self.center_retina.clear()
        self.center_face.clear()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(int(self.face_dim[0] * 0.8), int(self.face_dim[1] * 0.8)),
            maxSize=(int(self.face_dim[0] * 1.2), int(self.face_dim[1] * 1.2))
        )

        for (x, y, w, h) in faces:
            center_face = (x + w // 2, y + h // 2)
            roi_color = image[y:y + h, x:x + w]
            self.center_face.append((center_face, w, h))
            self.detect_eyes(roi_color, x, y, w, h)

    def detect_eyes(self, roi_color, x, y, w, h):
        left_open = False
        right_open = False
        roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
        eyes = self.eyeCascade.detectMultiScale(roi_gray,
                                                scaleFactor=1.1,
                                                minNeighbors=5,
                                                maxSize=(w // 2, h // 4),
                                                minSize=(w // 8, h // 8))
        for (ex, ey, ew, eh) in eyes:
            center_retina = (x + ex + ew // 2, y + ey + eh // 2)

            if y < center_retina[1] < y + h // 2:
                if self.set_center and len(self.center_eye) <= 2:
                    self.center_eye.append((center_retina, ew, eh))

                self.center_retina.append(center_retina)
                left_eye = center_retina[0] < x + w // 2

                if left_eye:
                    left_open = True
                else:
                    right_open = True

        self.open_left = left_open
        self.open_right = right_open

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
                self.map_image(img, left_eye, divs=self.divs)

            img = self.cat_images([self.eye_imgs['left'], self.eye_imgs['right']])
            self.eye_imgs['left'].clear()
            self.eye_imgs['right'].clear()

        self.eyes = img

    def map_image(self, src, left, divs=(12, 3)):
        img_gray = cv2.cvtColor(src.copy(), cv2.COLOR_RGB2GRAY)
        img_mapped_black = img_gray.copy()
        side = 'left' if left else 'right'

        if len(self.eye_imgs[side]) == 0:
            for n in divs:
                img_mapped_gray = self.divide_image(img_mapped_black.copy(), div=n)
                img_mapped_black = cv2.threshold(img_mapped_gray.copy(), self.thresh, 255, cv2.THRESH_BINARY)[1]

                if n == divs[0]:
                    self.eye_imgs[side].append(img_gray)
                self.eye_imgs[side].append(img_mapped_gray)
                self.eye_imgs[side].append(img_mapped_black)

    def divide_image(self, img, div):
        h = img.shape[0]
        w = img.shape[1]
        f_image = np.zeros([h, w])
        index = 0
        d = 0
        br_max = 255

        for n in range(div):
            for r in range(div):
                i = img[n * h // div:(n + 1) * h // div,
                    r * w // div: (r + 1) * w // div]
                br = cv2.mean(i)
                i.fill(br[0])

                if div <= 3:
                    if index in [0, 2, 6, 8]:
                        i.fill(255)
                    elif br[0] < br_max:
                        br_max = br[0]
                        i.fill(0)
                        self.thresh = br_max * 0.8
                        d = index
                else:
                    if r in [0, div - 1] or n in [0, div - 1]:
                        i.fill(255)
                    elif br[0] < br_max:
                        br_max = br[0]
                        self.thresh = br_max * 1.2

                index += 1
                f_image[n * h // div:(n + 1) * h // div, r * w // div: (r + 1) * w // div] = i
        self.direction = d

        return f_image

    @staticmethod
    def cat_images(img_list1, padding=10, scale=2):
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
                final_image[current_y:current_y + image.shape[1],
                current_x:image.shape[0] + current_x, 0] = image

                final_image[current_y:current_y + image.shape[1],
                current_x:image.shape[0] + current_x, 1] = image

                final_image[current_y:current_y + image.shape[1],
                current_x:image.shape[0] + current_x, 2] = image

                current_x += image.shape[0] + padding

            current_y += img_height + padding
            current_x = 0

        img_list1.clear()

        dim = (int(scale * final_image.shape[1]), int(scale * final_image.shape[0]))
        final_image = cv2.resize(final_image, dim, interpolation=cv2.INTER_AREA)

        return final_image

    def __del__(self):
        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
        # self.out.release()


def main():
    directions = ['Scanning ...', 'up', 0, 'left', 'center', 'right', 0, 'down', 0]
    max_samples = 9
    n_samples = 0
    samples = [0] * 9
    result = 0

    q1 = Queue()
    detector = ObjectDetection(q1, draw_frame=True)
    t = Thread(target=detector.main)
    t.start()

    engine = pyttsx3.init()

    while True:
        data = q1.get()
        q1.task_done()

        if data is False:
            break

        if n_samples < max_samples:
            n_samples += 1
            samples[data['Direction']] += 1
        else:
            n_samples = 0
            direction = samples.index(max(samples))
            samples = [0] * 9
            print('\rDirection: ' + str(directions[direction]), end='')
            # print('\nLeft Eye Opened: ' + str(data['Left']) +
            #       ' Right Eye Opened: ' + str(data['Right']), end='')
            if result != direction:
                result = direction
                if result != 4:
                    engine.say(str(directions[direction]))
                    engine.runAndWait()

    q1.join()
    t.join()


if __name__ == '__main__':
    # profile.run('main()', sort=2)
    main()
