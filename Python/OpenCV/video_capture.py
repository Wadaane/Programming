import cv2

video = cv2.VideoCapture(0)
record = False

# # Default resolutions of the frame are obtained.The default resolutions are system dependent.
# # We convert the resolutions from float to integer.
frame_width = int(video.get(3))
frame_height = int(video.get(4))

# # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter(
    'video.avi',
    cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
    30,
    (frame_width, frame_height))

while True:
    check, frame = video.read()

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Capturing", frame)

    # Write the frame into the file 'output.avi'
    if record:
        out.write(frame)

    # press 's' to toggle record
    if cv2.waitKey(30) & 0xFF == ord('s'):
        record = not record
    # Press 'q' to close
    elif cv2.waitKey(30) & 0xFF == ord('q'):
        break

video.release()
out.release()
cv2.destroyAllWindows()
