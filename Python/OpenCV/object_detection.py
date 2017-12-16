import cv2

eyeCascade = cv2.CascadeClassifier("models\haarcascade_eye.xml")
profileCascade = cv2.CascadeClassifier("models\haarcascade_profileface.xml")
smileCascade = cv2.CascadeClassifier("models\haarcascade_smile.xml")
faceCascade = cv2.CascadeClassifier("models\haarcascade_frontalface_default.xml")

video_capture = cv2.VideoCapture(0)


def detect_eyes(roi_color):
    roi_gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    eyes = eyeCascade.detectMultiScale(roi_gray)
    # Draw a rectangle around the eyes.
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)


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

        detect_eyes(roi_color)
        # detect_smiles(roi_color)


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


while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    detect_faces(frame)
    # detect_profiles(frame)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    fps = 10
    if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
