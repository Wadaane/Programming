import cv2
import serial
import numpy as np


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
    ret, frame = video_capture.read()
    ent = calc_entropy(frame)
    name = 'Images/Samples/{:02}_{}.jpg'.format(_i, ent)
    cv2.imwrite(name, frame)

    return frame, ent


def calc_entropy(src):
    img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()
    logs = np.log2(hist + 0.00001)

    _entropy = -1 * (hist * logs).sum()
    return _entropy


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
    entropy_prev = 0
    choice = True
    adjustment = 'inc', 'dec'

    while not _next:
        msg_arduino = mSerial.read_serial()
        if msg_arduino == str(pos):
            image, entropy = take_picture(pos)
            if entropy >= 6.2:
                mSerial.send_serial('next')
                _next = True
                pos += 1
            else:
                choice ^= entropy_prev >= entropy

                mSerial.send_serial(adjustment[choice])
                entropy_prev = entropy

        elif msg_arduino == 'Done':
            _run = False
            break

mSerial.close()
video_capture.release()
