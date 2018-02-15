from queue import Queue
from threading import Thread

import cv2
import numpy as np


class ObjectDetection:
    def __init__(self, q, draw_frame=True):
        self.eyeCascade = cv2.CascadeClassifier("..\models\haarcascade_eye.xml")
        self.faceCascade = cv2.CascadeClassifier("..\models\haarcascade_frontalface_default.xml")

        self.q = q
        self.max_width = 0
        self.max_height = 0
        self.thresh = 0
        self.draw_frame = draw_frame
        self.record = False
        self.set_center = False
        self.eye_imgs = {'left': [], 'right': []}
        self.video_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.fps = 30
        self.center_face = [(0, 0, 0, 0), ]
        self.center_eye = []
        self.center_retina = [(0, 0), ]

        # self.out = cv2.VideoWriter('video.avi',
        #                            cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
        #                            self.fps / 10,
        #                            (self.frame_width, self.frame_height))

    def detect_faces_eyes(self, image):
        self.center_retina.clear()
        self.center_face.clear()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            roi_color = image[y:y + h, x:x + w]
            self.center_face.append((x, y, w, h))
            self.detect_eyes(roi_color, x, y, h)

    def detect_eyes(self, roi_color, x, y, h):
        roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
        eyes = self.eyeCascade.detectMultiScale(roi_gray,
                                                scaleFactor=1.1,
                                                minNeighbors=5,
                                                maxSize=(h // 4, h // 4),
                                                minSize=(h // 8, h // 8))
        for (ex, ey, ew, eh) in eyes:
            if self.set_center and len(self.center_eye) <= 2:
                self.center_eye.append((x + ex + ew // 2,
                                        y + ey + eh // 2,
                                        ew, eh))
            self.center_retina.append((x + ex + ew // 2, y + ey + eh // 2))

    def draw(self, src):
        img = src.copy()
        for face in self.center_face:
            cv2.rectangle(img,
                          (face[0], face[1]),
                          (face[0] + face[2], face[1] + face[3]),
                          (0, 0, 0), 2)

        for eye in self.center_eye:
            cv2.rectangle(img,
                          (eye[0] - eye[2] // 2, eye[1] - eye[3] // 2),
                          (eye[0] + eye[2] // 2, eye[1] + eye[3] // 2),
                          (0, 0, 255), 2)

        for retina in self.center_retina:
            cv2.line(img, (retina[0] - 10, retina[1]),
                     (retina[0] + 10, retina[1]), (255, 0, 0), 2)
            cv2.line(img, (retina[0], retina[1] - 10),
                     (retina[0], retina[1] + 10), (255, 0, 0), 2)

        if self.draw_frame:
            cv2.imshow('Video', img)

        self.draw_eyes(src)

        # if self.record:
        #     self.out.write(img)

        key = cv2.waitKey(int(1000 / self.fps))
        if key == ord('s'):
            self.record = not self.record
            return True

        elif key in [ord('c'), 32]:
            self.set_center = True
            self.thresh = 0
            self.center_eye.clear()
            return True

        elif key in [ord('q'), ord('\x1b')] or (self.draw_frame and cv2.getWindowProperty('Video', 0) < 0):
            return False
        else:
            self.set_center = False
            return True

    def process(self):
        ret, frame = self.video_capture.read()
        frame = cv2.flip(frame, 1)

        self.detect_faces_eyes(frame)

        d = {
            'retinas': self.center_retina,
            'eyes': self.center_eye
        }

        run = self.draw(frame)
        if run:
            self.q.put(d)
        else:
            self.q.put(False)

        return run

    def main(self):
        run = True
        while run:
            run = self.process()

    def draw_eyes(self, src):
        img = np.zeros([128, 256])
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, 'Press Space Bar', (32, 64), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if len(self.center_eye) > 0:
            for center in self.center_eye:
                img = src[center[1] - center[3] // 2:center[1] + center[3] // 2,
                      center[0] - center[2] // 2:center[0] + center[2] // 2]
                middle = src.shape[1] // 2
                # print(center[0], middle, src.shape[1])
                self.map_image(img, center[0] < middle)

            if len(self.eye_imgs['left']) == 5 or len(self.eye_imgs['right']) == 5:
                img = self.cat_images([self.eye_imgs['left'], self.eye_imgs['right']])

        cv2.imshow('Eyes', img)
        self.eye_imgs['left'].clear()
        self.eye_imgs['right'].clear()

    def map_image(self, src, left):
        img_gray = cv2.cvtColor(src.copy(), cv2.COLOR_RGB2GRAY)

        img_mapped_gray4 = self.divide_image(img_gray.copy(), div=6)
        img_mapped_black4 = cv2.threshold(img_mapped_gray4.copy(), self.thresh, 255, cv2.THRESH_BINARY)[1]

        img_mapped_gray3 = self.divide_image(img_mapped_black4.copy(), div=3)
        img_mapped_black3 = cv2.threshold(img_mapped_gray3.copy(), self.thresh, 255, cv2.THRESH_BINARY)[1]

        side = 'left' if left else 'right'

        if len(self.eye_imgs[side]) == 0:
            self.eye_imgs[side].append(img_gray)
            self.eye_imgs[side].append(img_mapped_gray4)
            self.eye_imgs[side].append(img_mapped_black4)
            self.eye_imgs[side].append(img_mapped_gray3)
            self.eye_imgs[side].append(img_mapped_black3)

    def divide_image(self, img, div):
        h = img.shape[0]
        w = img.shape[1]
        f_image = np.zeros([h, w])
        index = 0
        br_max = 255

        for n in range(div):
            for r in range(div):
                i = img[n * h // div:(n + 1) * h // div,
                    r * w // div: (r + 1) * w // div]
                br = cv2.mean(i)
                i.fill(br[0])

                if div == 3:
                    if index in [0, 2, 6, 8]:
                        i.fill(255)
                    elif br[0] < br_max:
                        br_max = br[0]
                        i.fill(0)
                        self.thresh = br_max * 0.8
                    else:
                        pass
                        # i.fill(255)

                    # if self.set_center and index == 4:
                    #     br_max = br[0]
                    #     self.thresh = br_max * 0.85
                else:
                    if r in [0, div - 1] or n in [0, div - 1]:
                        i.fill(255)
                    elif br[0] < br_max:
                        br_max = br[0]
                        self.thresh = br_max * 1.2  # More is more dark

                index += 1
                f_image[n * h // div:(n + 1) * h // div, r * w // div: (r + 1) * w // div] = i

        return f_image

    def cat_images(self, img_list1):
        padding = 10
        max_width = 0
        max_height = []

        for img_list in img_list1:
            for img in img_list:
                max_height.append(img.shape[0])
                max_width += img.shape[1]

        if np.size(max_height) > 0:
            self.max_height = max(np.max(max_height), self.max_height)
            self.max_width = max(max_width, self.max_width)

        # create a new array with a size large enough to contain all the images
        final_image = np.zeros((self.max_height, self.max_width + padding), dtype=np.uint8)

        current_x = 0  # keep track of where your current image was last placed in the y coordinate

        for img_list in img_list1:
            for image in img_list:
                final_image[:image.shape[1], current_x:image.shape[0] + current_x] = image
                current_x += image.shape[0]
            img_list.clear()
            current_x += padding

        return final_image

    def __del__(self):
        # When everything is done, release the capture
        self.video_capture.release()
        cv2.destroyAllWindows()
        # self.out.release()


if __name__ == '__main__':
    q1 = Queue()
    detector = ObjectDetection(q1, draw_frame=True)
    t = Thread(target=detector.main)
    t.start()

    while True:
        data = q1.get()
        q1.task_done()

        if data is False:
            break

        # print(data)

    q1.join()
    t.join()
