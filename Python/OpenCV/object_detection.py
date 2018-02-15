import cv2


class ObjectDetection:
    def __init__(self):
        self.eyeCascade = cv2.CascadeClassifier("models\haarcascade_eye.xml")
        self.profileCascade = cv2.CascadeClassifier("models\haarcascade_profileface.xml")
        self.smileCascade = cv2.CascadeClassifier("models\haarcascade_smile.xml")
        self.faceCascade = cv2.CascadeClassifier("models\haarcascade_frontalface_default.xml")

        self.record = False
        self.set_center = False
        self.video_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.video_capture.get(3))
        self.frame_height = int(self.video_capture.get(4))
        self.fps = 30
        self.center = [(0, 0), (0, 0)]
        self.center_eye = [(0, 0), (0, 0)]
        self.eye_dim = 0, 0

        self.out = cv2.VideoWriter('video.avi',
                                   cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                   self.fps / 10,
                                   (self.frame_width, self.frame_height))

    def detect_eyes(self, roi_color, x, y, h):
        roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
        eyes = self.eyeCascade.detectMultiScale(roi_gray,
                                                scaleFactor=1.1,
                                                minNeighbors=5,
                                                maxSize=(h // 4, h // 4),
                                                minSize=(h // 8, h // 8))
        # Draw a rectangle around the eyes.
        index = 0
        for (ex, ey, ew, eh) in eyes:
            # global center, set_center, eye_dim
            if self.set_center:
                self.center[index] = (x + ex + ew // 2, y + ey + eh // 2)
                self.eye_dim = ew, eh
                index += 1
                if index >= 2:
                    self.set_center = False
                    self.center_eye.append((x + ex + ew // 2, y + ey + eh // 2))

    def detect_smiles(self, roi_color):
        roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
        smiles = self.smileCascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50))
        # Draw a rectangle around the smiles.
        for (sx, sy, sw, sh) in smiles:
            cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (255, 0, 0), 2)

    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2)
            roi_color = image[y:y + h, x:x + w]

            self.detect_eyes(roi_color, x, y, h)

    def detect_profiles(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        profiles = self.profileCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        # Draw a rectangle around the profiles.
        for (px, py, pw, ph) in profiles:
            cv2.rectangle(image, (px, py), (px + pw, py + ph), (255, 255, 255), 2)

    def draw(self, img):
        for i in self.center:
            cv2.rectangle(img,
                          (i[0] - self.eye_dim[0] // 2, i[1] - self.eye_dim[1] // 2),
                          (i[0] + self.eye_dim[0] // 2, i[1] + self.eye_dim[1] // 2),
                          (0, 0, 255), 2)

        for index in self.center_eye:
            cv2.line(img, (index[0] - 10, index[1]),
                     (index[0] + 10, index[1]), (255, 0, 0), 2)
            cv2.line(img, (index[0], index[1] - 10),
                     (index[0], index[1] + 10), (255, 0, 0), 2)
            self.center_eye.clear()

    def process(self):
        # global record, set_center

        # Capture frame-by-frame
        ret, frame = self.video_capture.read()
        frame = cv2.flip(frame, 1)

        self.detect_faces(frame)
        # detect_profiles(frame)

        self.draw(frame)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if self.record:
            self.out.write(frame)

        if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('s'):
            self.record = not self.record
            return True

        elif cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('c'):
            self.set_center = True
            return True

        elif cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
            return False
        else:
            return True

    def __del__(self):
        # When everything is done, release the capture
        self.video_capture.release()
        self.out.release()
        cv2.destroyAllWindows()


def main():
    detector = ObjectDetection()
    run = True
    while run:
        run = detector.process()


if __name__ == '__main__':
    main()
