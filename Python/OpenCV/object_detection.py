import cv2

eyeCascade = cv2.CascadeClassifier("haarcascade_eye.xml")
profileCascade = cv2.CascadeClassifier("haarcascade_profileface.xml")
smileCascade = cv2.CascadeClassifier("haarcascade_smile.xml")
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces.
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        # Detect eyes.
        eyes = eyeCascade.detectMultiScale(roi_gray)
        # Draw a rectangle around the eyes.
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)

        # Detect smiles.
        smiles = smileCascade.detectMultiScale(roi_gray)
        # Draw a rectangle around the smiles.
        for (sx, sy, sw, sh) in smiles:
            cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (255, 0, 0), 2)

    # Detect profiles.
    profiles = profileCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    # Draw a rectangle around the profiles.
    for (px, py, pw, ph) in profiles:
        cv2.rectangle(frame, (px, py), (px + pw, py + ph), (255, 255, 255), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    fps = 10
    if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
