from queue import Queue
from threading import Thread

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from object_detection import ObjectDetection

q = Queue()
detector = ObjectDetection(q, draw_frame=True)
t = Thread(target=detector.main)
t.start()

fig = plt.figure()
ax = plt.axes(xlim=(0, detector.frame_width),
              ylim=(0, detector.frame_height))

line, = plt.plot([], [], 'ro', animated=True)
rectangle1 = Rectangle((0, 0),
                       0,
                       0,
                       fill=False)

rectangle2 = Rectangle((0, 0),
                       0,
                       0,
                       fill=False)
ax.add_patch(rectangle1)
ax.add_patch(rectangle2)


def init():
    line.set_data([], [])
    return line,


def animate(i):
    data = q.get()
    q.task_done()

    print(data)
    if not data:
        anim.event_source.stop()
    else:
        line.set_data([], [])
        x = []
        y = []
        if len(data['eyes']) > 0:
            eye = data['eyes'][0]
            rectangle1.set_bounds(eye[0] - eye[2] // 2,
                                  detector.frame_height - eye[1] - eye[3] // 2,
                                  eye[2],
                                  eye[3])
        if len(data['eyes']) > 1:
            eye2 = data['eyes'][1]
            rectangle2.set_bounds(eye2[0] - eye2[2] // 2,
                                  detector.frame_height - eye2[1] - eye2[3] // 2,
                                  eye2[2],
                                  eye2[3])

        for retina in data['retinas']:
            x.append(retina[0])
            y.append(detector.frame_height - retina[1])
        line.set_data(x, y)
    return line, rectangle1, rectangle2


print("set animation")
anim = FuncAnimation(fig, animate, init_func=init,
                     frames=33, interval=33, blit=True)

print("plot")
plt.show()

q.join()
t.join()
