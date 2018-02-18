from queue import Queue
from threading import Thread

import cv2
import numpy as np
import pyttsx3


# import profile


class ObjectDetection:
    def __init__(self, q, draw_frame=True):
        self.ver_strings = ['Center', 'Top', 'Bottom']
        self.hor_strings = ['Center', 'Left', 'Right']
        self.directions = ['Center', 'left', 'right', 'Bottom', 'Top', 'Press Space']
        self.direction = [0] * 10
        self.hor_directions = [0] * 3
        self.ver_directions = [0] * 3
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
        self.centered_img = []
        self.fixed_eye = True
        self.center_face = []
        self.center_eye = []
        self.center_retina = []
        self.calibrate = False
        self.calibration_step = -1
        self.iris = [[]] * 5
        self.calibrated_center = [(0, 0)] * 5
        self.calibration_finished = False
        self.center_iris = []

    def main(self):
        while True:
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)

            self.detect_faces_eyes(frame)
            self.detect_eye_move(frame)
            self.detect_eye_move2()

            if len(self.center_face) > 0 and len(self.center_eye) > 0:
                self.face_dim = self.center_face[0][1], self.center_face[0][2]

            if self.draw_frame:
                self.draw(frame)

            d = {
                'Direction': self.direction.index(max(self.direction)),
                'Left': self.open_left,
                'Right': self.open_right,
                'Horizontal': self.hor_directions.index(max(self.hor_directions)),
                'Vertical': self.ver_directions.index(max(self.ver_directions)),
                'Calibration_finished': self.calibration_finished
            }

            self.direction.clear()
            self.direction = [0] * 10
            self.hor_directions.clear()
            self.hor_directions = [0] * 3
            self.ver_directions.clear()
            self.ver_directions = [0] * 3

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
        if self.centered_img is not None and len(self.centered_img) > 0:
            cv2.imshow('Eyes1', self.cat_images([self.centered_img]))
            self.centered_img.clear()

    def control_input(self):
        if not self.fixed_eye:
            detected = False

            for center_retina in self.center_retina:
                for center in self.center_eye:
                    detected |= center[0][0] - center[1] // 2 < center_retina[0] < center[0][0] + center[1] // 2 and \
                                center[0][1] - center[2] // 2 < center_retina[1] < center[0][1] + center[2] // 2

            if not detected:
                self.direction[9] = -1

        key = cv2.waitKey(1000 // self.fps)

        if key in [ord('c'), 32] or self.direction[9] == -1:
            # self.scan()
            if self.calibrate:
                self.calibration_step += 1
                if self.calibration_step >= len(self.calibrated_center):
                    self.calibration_step = -1
                    self.calibrate = False
                    self.calibration_finished = True
            elif self.calibration_step == -1:
                self.scan()
                self.calibrate = True
                self.calibration_finished = False
            print("Calibration:", self.directions[self.calibration_step])

            return True

        elif key in [ord('q'), ord('\x1b')] or (self.draw_frame and cv2.getWindowProperty('Video', 0) < 0):
            return False
        else:
            self.set_center = False
            return True

    def calibration(self):
        center_x = np.array(self.iris[self.calibration_step])
        center_y = np.array(self.iris[self.calibration_step])
        x = int(center_x.mean())
        y = int(center_y.mean())
        self.calibrated_center[self.calibration_step] = x, y

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
                self.map_image(img, left_eye)

            img = self.cat_images([self.eye_imgs['left'], self.eye_imgs['right']])
            self.eye_imgs['left'].clear()
            self.eye_imgs['right'].clear()

        self.eyes = img

    def detect_eye_move2(self):
        if self.calibration_finished:
            c_center = self.calibrated_center[0]
            c_left = self.calibrated_center[1]
            c_right = self.calibrated_center[2]
            c_bottom = self.calibrated_center[3]
            c_top = self.calibrated_center[4]

            b_left = c_left[0]  # + (c_center[0] - c_left[0])//2
            b_right = c_right[0]  # c_center[0] + (c_right[0] - c_center[0])//2

            b_bottom = c_bottom[1]  # c_center[1] + (c_bottom[1] - c_center[1]) // 2
            b_top = c_top[1]  # + (c_center[1] - c_top[1]) // 2

            for center in self.center_iris:
                hor = 0
                if center[0] < b_left:
                    self.hor_directions[1] += 1
                    hor = 1
                    # print(self.directions[1], end=': ')
                elif center[0] > b_right:
                    self.hor_directions[2] += 1
                    hor = 2
                    # print(self.directions[2], end=': ')
                else:
                    self.hor_directions[0] += 1
                    # print(self.directions[0], end=': ')
                print(str(b_left) + ' ' + str(center[0]) + ' ' + str(b_right), self.hor_strings[hor])

                ver = 0
                if center[1] < b_top:
                    self.ver_directions[1] += 1
                    ver = 1
                    # print(self.directions[4])
                elif center[1] > b_bottom:
                    self.ver_directions[2] += 1
                    ver = 2
                    # print(self.directions[3])
                else:
                    self.ver_directions[0] += 1
                    # print(self.directions[0])

                print(str(b_top) + ' ' + str(center[1]) + ' ' + str(b_bottom), self.ver_strings[ver] + '\n', )
                # print(self.hor_strings[self.hor_directions.index(max(self.hor_directions))],
                #       self.ver_strings[self.ver_directions.index(max(self.ver_directions))])

            self.center_iris.clear()

    def map_image(self, src, left):
        divs = self.divs
        img_gray = cv2.cvtColor(src.copy(), cv2.COLOR_RGB2GRAY)
        img_mapped_black = img_gray.copy()
        side = 'left' if left else 'right'

        if len(self.eye_imgs[side]) == 0:
            self.divide_image(img_mapped_black, div=divs[0])
            img_mapped_black = cv2.threshold(img_mapped_black.copy(), self.thresh * 1.2, 255, cv2.THRESH_BINARY)[1]
            image_direction = self.divide_image(img_mapped_black.copy(), div=divs[1], return_image=True)

            self.get_draw_center(img_gray, img_mapped_black.copy())
            self.eye_imgs[side].append(img_gray)
            self.eye_imgs[side].append(img_mapped_black.copy())
            self.eye_imgs[side].append(image_direction)

    def divide_image(self, img, div, return_image=False):
        h = img.shape[0]
        w = img.shape[1]
        index = 0
        d = 0
        br_max = 255

        for n in range(div):
            for r in range(div):
                i = img[n * h // div:(n + 1) * h // div,
                    r * w // div: (r + 1) * w // div]
                br = cv2.mean(i)
                if not return_image and (r in [0, 1, div - 2, div - 1] or
                                         n in [0, 1, div - 2, div - 1]):
                    i.fill(255)

                if br[0] < br_max:
                    br_max = br[0]
                    self.thresh = br_max

        if return_image:
            f_image = np.zeros([h, w])
            for n in range(div):
                for r in range(div):
                    i = img[n * h // div:(n + 1) * h // div,
                        r * w // div: (r + 1) * w // div]
                    br = cv2.mean(i)
                    i.fill(br[0])

                    if br[0] <= br_max:
                        i.fill(0)
                        d = index
                    else:
                        i.fill(255)

                    index += 1
                    f_image[n * h // div:(n + 1) * h // div, r * w // div: (r + 1) * w // div] = i

            self.direction[d] += 1
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
                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 0] = image

                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 1] = image

                final_image[current_y:current_y + image.shape[1], current_x:image.shape[0] + current_x, 2] = image

                current_x += image.shape[0] + padding

            current_y += img_height + padding
            current_x = 0

        img_list1.clear()

        dim = (int(scale * final_image.shape[1]), int(scale * final_image.shape[0]))
        final_image = cv2.resize(final_image, dim, interpolation=cv2.INTER_AREA)

        return final_image

    def get_draw_center(self, src, img, radius=7):
        x_list = []
        y_list = []

        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                if img[y, x] == 0:
                    x_list.append(x)
                    y_list.append(y)

        if len(x_list) > 0:
            center = (min(x_list) + (max(x_list) - min(x_list)) // 2,
                      min(y_list) + (max(y_list) - min(y_list)) // 2)

            if self.calibrate:
                self.iris[self.calibration_step].append(center)
                if len(self.iris[self.calibration_step]) > 50:
                    self.calibration()
                    self.iris[self.calibration_step].clear()
                cv2.circle(src, self.calibrated_center[self.calibration_step], radius, 255, thickness=-1)
            else:
                cv2.circle(src, center, radius, 255, thickness=-1)
                self.center_iris.append(center)

    def __del__(self):
        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
        # self.out.release()


def main():
    # directions = ['Top Left', 'Top', 'Top Right',
    #               'left', 'center', 'right',
    #               'Bottom Left', 'Bottom', 'Bottom Right',
    #               'Scanning ...']
    bi_directions = [['Center', 'Left', 'Right'], ['Center', 'Top', 'Bottom']]
    max_samples = 1
    n_samples = 0
    samples = [0] * 9
    hor_samples = [0] * 3
    ver_samples = [0] * 3
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

        # print(data)

        calibration_finished = data['Calibration_finished']

        if calibration_finished:
            if n_samples < max_samples:
                n_samples += 1
                samples[data['Direction']] += 1
                hor_samples[data['Horizontal']] += 1
                ver_samples[data['Vertical']] += 1
            else:
                n_samples = 0
                direction = samples.index(max(samples))
                hor = hor_samples.index(max(hor_samples))
                ver = ver_samples.index(max(ver_samples))
                samples = [0] * 9
                # print('\rDirection: ' + str(directions[direction]), end='')
                # print('Hor: ' + str(bi_directions[0][hor]), end=' ')
                # print('Ver: ' + str(bi_directions[1][ver]), end='\n\n')
                # print('\nLeft Eye Opened: ' + str(data['Left']) +
                #       ' Right Eye Opened: ' + str(data['Right']), end='')
                if result != direction:
                    result = direction
                    if result != 4:
                        pass
                        # engine.say(str(directions[direction]))
                        # engine.say(str(bi_directions[0][hor]))
                        # engine.say(str(bi_directions[1][ver]))
                        # engine.runAndWait()

    q1.join()
    t.join()


if __name__ == '__main__':
    # profile.run('main()', sort=2)
    main()
