from math import pi, atan2, sin, cos, degrees, sqrt, radians
from tkinter import *


class TkinterPedro(Canvas):

    def __init__(self, unit, callback, range_hand, range_forearm, range_base):
        super().__init__()

        self.range_base = range_base
        self.range_hand = range_hand
        self.range_forearm = range_forearm
        self.angles = StringVar()
        self.angles.trace('w', callback)
        self.speed = 0.1
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

        self.angle_hand = self.range_hand[0]
        self.angle_forearm = self.range_forearm[0]
        self.angle_elbow = - radians(180 - self.range_forearm[0])
        self.angle_base = self.range_base[0]

        x = self.length_forearm * cos(self.angle_elbow)
        y = self.length_forearm * sin(self.angle_elbow)
        self.elbow = x + self.origin[0], y + self.origin[1]

        y = self.length_hand * sin(- radians(self.range_hand[0]) + self.angle_elbow)
        x = self.length_hand * cos(- radians(self.range_hand[0]) + self.angle_elbow)
        self.end = - x + self.elbow[0], - y + self.elbow[1]

        self.angle_end = self.get_angle(self.origin, self.end)

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

        self.slider = Scale(self.master, from_=0, to=(range_base[1] - range_base[0]),
                            orient=HORIZONTAL,
                            length=self.canvas_width,
                            command=self.slider_clicked,
                            font=("Purisa", self.text_size),
                            label='Base Angle: ')
        self.create_window(self.origin[0], self.canvas_height + self.SIZE / 10,
                           window=self.slider, anchor=S)

        self.selected = self.hand
        self.bind("<B1-Motion>", self.left_drag)
        self.bind("<ButtonPress-1>", self.left_press)

    def lerp(self, start, end, percent):
        return start + percent * (end - start)

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
        try:
            self.rotate(self.gettags(self.selected)[0], (event.x, event.y))
        finally:
            self.draw()

    def rotate(self, tag, event):
        if tag == 'hand':
            hypotenuse = self.length_hand
            angle = self.get_angle(self.elbow, event)
            y = hypotenuse * sin(angle)
            x = hypotenuse * cos(angle)

            end = x + self.elbow[0], y + self.elbow[1]
            angle_end = self.get_angle(self.origin, end)
            #  Use cosine and sine rule to get an accurate Hand angle (between Hand and Forearm)
            sin_hand = ((self.length(self.origin, end))
                        / (self.length(self.elbow, end))) * sin(self.angle_elbow - angle_end)
            cos_hand = (self.length_hand ** 2
                        + self.length_forearm ** 2
                        - self.length(self.origin, end) ** 2) / (2 * self.length_hand * self.length_forearm)

            angle = self.get_degrees(atan2(sin_hand, cos_hand))

            if self.range_hand[0] <= angle <= self.range_hand[1] + 1:
                self.angle_hand = int(angle)
                self.end = end
                self.angle_end = angle_end

        if tag == 'forearm':
            angle = self.get_angle(self.origin, event)
            angle_end = angle - (self.angle_elbow - self.angle_end)
            angle_elbow = angle

            hypotenuse = self.length_forearm
            x = hypotenuse * cos(angle_elbow)
            y = hypotenuse * sin(angle_elbow)
            elbow = x + self.origin[0], y + self.origin[1]

            # Update Hand
            hypotenuse = self.length(self.origin, self.end)
            x3 = hypotenuse * cos(angle_end)
            y3 = hypotenuse * sin(angle_end)
            end = x3 + self.origin[0], y3 + self.origin[1]

            #  Use cosine and sine rule to get an accurate Hand angle (between Hand and Forearm)
            sin_hand = ((self.length(self.origin, end))
                        / self.length_hand) * sin(angle_elbow - angle_end)
            cos_hand = (self.length_hand ** 2
                        + self.length_forearm ** 2
                        - self.length(self.origin, end) ** 2) / (2 * self.length_hand * self.length_forearm)

            angle = self.get_degrees(- angle_elbow + pi)
            angle1 = self.get_degrees(atan2(sin_hand, cos_hand))

            if self.range_forearm[0] <= angle <= self.range_forearm[1] + 1:
                self.angle_forearm = int(angle)
                self.angle_hand = int(angle1)
                self.angle_end = angle_end
                self.angle_elbow = angle_elbow
                self.elbow = elbow
                self.end = end

    def draw(self):
        self.length_forearm = self.length(self.origin, self.elbow)
        self.angles.set('{} {} {} '.format(self.angle_base - self.range_base[0],
                                           self.angle_forearm - self.range_forearm[0],
                                           self.angle_hand - self.range_hand[0]))

        #  Forearm
        self.coords(self.forearm,
                    self.origin[0],
                    self.origin[1],
                    self.elbow[0],
                    self.elbow[1])

        #  Hand
        self.coords(self.hand,
                    self.elbow[0],
                    self.elbow[1],
                    self.end[0],
                    self.end[1])
        self.itemconfig(self.text_base, text='Base: {:>7.0f}°'.format(self.angle_base - self.range_base[0]))
        self.itemconfig(self.text_forearm, text='Forearm: {:>3.0f}°'.format(self.angle_forearm - self.range_forearm[0]))
        self.itemconfig(self.text_hand, text='Hand: {:>7.0f}°'.format(self.angle_hand - self.range_hand[0]))

        self.coords(self.oval_elbow,
                    self.elbow[0] - self.radius,
                    self.elbow[1] - self.radius,
                    self.elbow[0] + self.radius,
                    self.elbow[1] + self.radius)


def main():
    master = Tk()
    master.title("Pedro")
    # master.geometry('800x600')
    # master.resizable(False, False)
    master.bind("<Escape>", lambda e: master.quit())

    canvas = TkinterPedro(unit=50,
                          callback=lambda *args: print(canvas.angles.get()),
                          range_hand=(45, 215),
                          range_forearm=(0, 170),
                          range_base=(0, 170))
    canvas.pack(expand=False, fill=NONE)

    message = Label(master, text="Click and Drag to move")
    message.pack()  # side=BOTTOM

    mainloop()


if __name__ == '__main__':
    main()
