import cv2
import serial


class SerialComm:
    def __init__(self):
        self.connected = False
        self.port = self.connect()

    def connect(self):
        self.connected = False
        try:
            port = serial.Serial('COM8', baudrate=9600, timeout=1)
            self.connected = True
            return port
        except:
            # print('No Arduino')
            return None

    def read_serial(self):
        res = ''
        try:
            res = self.port.readline().decode()
        except:
            self.port = self.connect()
        finally:
            return res

    def send_serial(self, text):
        text += '#'
        try:
            self.port.write(text.encode())
        except:
            self.port = self.connect()

    def close(self):
        self.port.close()


def take_picture(_i):
    name = 'Images/Samples/{:02}.jpg'.format(_i)
    ret, frame = video_capture.read()
    cv2.imwrite(name, frame)


width = 2592
height = 1944
video_capture = cv2.VideoCapture(1)
mSerial = SerialComm()

mSerial.send_serial('start')
video_capture.set(3, width)
video_capture.set(4, height)

_ret, _frame = video_capture.read()
mSerial.send_serial('run')

_run = True
pos = 1

while _run:
    _next = False
    while not _next:
        msg_arduino = mSerial.read_serial()
        if msg_arduino == str(pos):
            take_picture(pos)
            mSerial.send_serial('next')
            _next = True
            pos += 1
        elif msg_arduino == 'Done':
            _run = False
            break

mSerial.close()
video_capture.release()

# while True:
#     print('Hello Matlab:')
