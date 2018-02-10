import cv2

# from matplotlib import pyplot as plt


eyeCascade = cv2.CascadeClassifier("models\haarcascade_eye.xml")
profileCascade = cv2.CascadeClassifier("models\haarcascade_profileface.xml")
smileCascade = cv2.CascadeClassifier("models\haarcascade_smile.xml")
faceCascade = cv2.CascadeClassifier("models\haarcascade_frontalface_default.xml")

record = False
set_center = False
video_capture = cv2.VideoCapture(0)
frame_width = int(video_capture.get(3))
frame_height = int(video_capture.get(4))
fps = 30
center = [(0, 0), (0, 0)]
center_eye = [(0, 0), (0, 0)]
eye_dim = 0, 0

out = cv2.VideoWriter('video.avi',
                      cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                      fps / 10,
                      (frame_width, frame_height))


def detect_eyes(roi_color, x, y, h):
    roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    eyes = eyeCascade.detectMultiScale(roi_gray,
                                       scaleFactor=1.1,
                                       minNeighbors=5,
                                       maxSize=(h // 4, h // 4),
                                       minSize=(h // 8, h // 8))
    # Draw a rectangle around the eyes.
    index = 0
    for (ex, ey, ew, eh) in eyes:
        global center, set_center, eye_dim
        if set_center:
            center[index] = (x + ex + ew // 2, y + ey + eh // 2)
            eye_dim = ew, eh
            index += 1
            if index >= 2:
                set_center = False
        center_eye.append((x + ex + ew // 2, y + ey + eh // 2))


def detect_smiles(roi_color):
    roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    smiles = smileCascade.detectMultiScale(
        roi_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50))
    # Draw a rectangle around the smiles.
    for (sx, sy, sw, sh) in smiles:
        cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (255, 0, 0), 2)


def detect_faces(image):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2)
        roi_color = image[y:y + h, x:x + w]

        detect_eyes(roi_color, x, y, h)


def detect_profiles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    profiles = profileCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    # Draw a rectangle around the profiles.
    for (px, py, pw, ph) in profiles:
        cv2.rectangle(image, (px, py), (px + pw, py + ph), (255, 255, 255), 2)


def draw(img):
    for i in center:
        cv2.rectangle(img,
                      (i[0] - eye_dim[0] // 2, i[1] - eye_dim[1] // 2),
                      (i[0] + eye_dim[0] // 2, i[1] + eye_dim[1] // 2),
                      (0, 0, 255), 2)

    for index in center_eye:
        cv2.line(img, (index[0] - 10, index[1]),
                 (index[0] + 10, index[1]), (255, 0, 0), 2)
        cv2.line(img, (index[0], index[1] - 10),
                 (index[0], index[1] + 10), (255, 0, 0), 2)
    center_eye.clear()


while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    frame = cv2.flip(frame, 1)

    detect_faces(frame)
    # detect_profiles(frame)

    draw(frame)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if record:
        out.write(frame)

    if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('s'):
        record = not record
        # plt.imshow(frame)
        # plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        # plt.show()

    elif cv2.waitKey(int(1000 / fps)) & 0xFF == ord('c'):
        set_center = True

    elif cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
out.release()
cv2.destroyAllWindows()
