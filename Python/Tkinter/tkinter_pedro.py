from math import pi, atan2, sin, cos, degrees, sqrt
from tkinter import *


class TkinterPedro(Canvas):

    def __init__(self, unit, callback):
        super().__init__()

        self.angles = StringVar()
        self.angles.trace('w', callback)
        self.bg = 'white'
        self.SIZE = unit
        self.text_size = int(self.SIZE / 6)
        self.canvas_width = 7 * self.SIZE
        self.canvas_height = 6 * self.SIZE
        self.config(width=self.canvas_width, height=self.canvas_height, bg=self.bg)

        self.radius = self.SIZE / 20
        self.length_forearm = 2 * self.SIZE
        self.length_hand = self.SIZE
        self.origin = [self.canvas_width / 2, self.canvas_height - 2.25 * self.SIZE]
        self.elbow = [self.origin[0] - self.length_forearm, self.origin[1]]
        self.end = [self.elbow[0] + self.length_hand, self.elbow[1]]

        self.base = self.create_line(self.canvas_width / 2, self.canvas_height,
                                     self.origin[0], self.origin[1],
                                     fill='black', width=self.SIZE, cap=ROUND,
                                     tag='base')
        self.forearm = self.create_line(self.origin[0], self.origin[1],
                                        self.elbow[0], self.elbow[1],
                                        fill='#000080', width=self.SIZE / 2, cap=ROUND,
                                        tag='forearm')
        self.hand = self.create_line(self.elbow[0], self.elbow[1],
                                     self.end[0], self.end[1],
                                     fill='black', width=self.SIZE / 4, cap=ROUND,
                                     tag='hand')
        self.oval_elbow = self.create_oval(-self.radius + self.elbow[0], -self.radius + self.elbow[1],
                                           self.radius + self.elbow[0], self.radius + self.elbow[1],
                                           fill='red')
        self.oval_origin = self.create_oval(-2 * self.radius + self.origin[0], -2 * self.radius + self.origin[1],
                                            2 * self.radius + self.origin[0], 2 * self.radius + self.origin[1],
                                            fill='red')
        self.text_forearm = self.create_text((10, self.text_size),
                                             anchor=NW,
                                             font=("Purisa", self.text_size),
                                             text='Forearm: {:>3.0f}°'.format(0))
        self.text_hand = self.create_text((10, 2 * 1.3 * self.text_size),
                                          anchor=NW,
                                          font=("Purisa", self.text_size),
                                          text='Hand: {:>7.0f}°'.format(0))
        self.text_base = self.create_text((10, 3 * 1.3 * self.text_size),
                                          anchor=NW,
                                          font=("Purisa", self.text_size),
                                          text='Base: {:>7.0f}°'.format(0))

        self.slider = Scale(self.master, from_=0, to=180,
                            orient=HORIZONTAL,
                            length=self.canvas_width,
                            command=self.slider_clicked,
                            font=("Purisa", self.text_size),
                            label='Base Angle: ')
        self.create_window(self.origin[0], self.canvas_height + self.SIZE / 10,
                           window=self.slider, anchor=S)

        self.angle_hand = self.get_angle(self.elbow, self.end)
        self.angle_forearm = self.get_angle(self.origin, self.elbow)
        self.angle_end = pi
        self.angle_elbow = pi
        self.angle_base = 0
        self.selected = self.hand
        self.bind("<B1-Motion>", self.left_drag)
        self.bind("<ButtonPress-1>", self.left_press)

    @staticmethod
    def get_degrees(angle):
        angle = - degrees(angle)
        if angle <= 0:
            angle = 360 + angle
            angle %= 360

        return angle

    @staticmethod
    def get_angle(origin, end):
        angle = atan2((end[1] - origin[1]),
                      (end[0] - origin[0]))
        return angle

    @staticmethod
    def length(origin, end):
        return sqrt((end[0] - origin[0]) ** 2
                    + (end[1] - origin[1]) ** 2)

    def slider_clicked(self, event):
        self.angle_base = self.slider.get()
        self.draw()

    def left_press(self, event):
        self.selected = self.find_closest(event.x, event.y)

    def left_drag(self, event):
        self.rotate(self.gettags(self.selected)[0], (event.x, event.y))
        self.draw()

    def rotate(self, tag, event):
        if tag == 'hand':
            hypotenuse = self.length(self.elbow, self.end)
            angle = self.get_angle(self.elbow, event)
            y = hypotenuse * sin(angle)
            x = hypotenuse * cos(angle)

            self.end = x + self.elbow[0], y + self.elbow[1]
            self.angle_end = self.get_angle(self.origin, self.end)

        if tag == 'forearm':
            angle0 = self.get_angle(self.origin, event)
            self.angle_end = angle0 - (self.angle_elbow - self.angle_end)
            self.angle_elbow = angle0

            hypotenuse = self.length(self.origin, self.elbow)
            x = hypotenuse * cos(self.angle_elbow)
            y = hypotenuse * sin(self.angle_elbow)
            self.elbow = x + self.origin[0], y + self.origin[1]

            # Update Hand
            hypotenuse = self.length(self.origin, self.end)
            x3 = hypotenuse * cos(self.angle_end)
            y3 = hypotenuse * sin(self.angle_end)
            self.end = x3 + self.origin[0], y3 + self.origin[1]

        #  Use cosine and sine rule to get an accurate Hand angle (between Hand and Forearm)
        sin_hand = ((self.length(self.origin, self.end))
                    / (self.length(self.elbow, self.end))) * sin(self.angle_elbow - self.angle_end)
        cos_hand = (self.length_hand ** 2
                    + self.length_forearm ** 2
                    - self.length(self.origin, self.end) ** 2) / (2 * self.length_hand * self.length_forearm)
        self.angle_hand = self.get_degrees(atan2(sin_hand, cos_hand))
        self.angle_forearm = self.get_degrees(- self.angle_elbow + pi)

    def draw(self):
        self.length_forearm = self.length(self.origin, self.elbow)

        #  Forearm
        self.coords(self.forearm,
                    self.origin[0],
                    self.origin[1],
                    self.elbow[0],
                    self.elbow[1])
        self.itemconfig(self.text_forearm, text='Forearm: {:>3.0f}°'.format(self.angle_forearm))

        #  Hand
        self.coords(self.hand,
                    self.elbow[0],
                    self.elbow[1],
                    self.end[0],
                    self.end[1])
        self.itemconfig(self.text_hand, text='Hand: {:>7.0f}°'.format(self.angle_hand))
        self.itemconfig(self.text_base, text='Base: {:>7.0f}°'.format(self.angle_base))

        self.coords(self.oval_elbow,
                    self.elbow[0] - self.radius,
                    self.elbow[1] - self.radius,
                    self.elbow[0] + self.radius,
                    self.elbow[1] + self.radius)

        self.angles.set((int(self.angle_base), int(self.angle_forearm), int(self.angle_hand)))


def main():
    master = Tk()
    master.title("Pedro")
    # master.geometry('800x600')
    # master.resizable(False, False)
    master.bind("<Escape>", lambda e: master.quit())

    canvas = TkinterPedro(unit=75, callback=lambda a, b, c: print(canvas.angles.get()))
    canvas.pack(expand=False, fill=NONE)

    message = Label(master, text="Click and Drag to move")
    message.pack()  # side=BOTTOM

    mainloop()


if __name__ == '__main__':
    main()
