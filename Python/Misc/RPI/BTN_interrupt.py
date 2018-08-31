#! /usr/bin/env python

import RPi.GPIO as GPIO
import time

BTN = 32
LED = 36

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT, initial=GPIO.HIGH)

counter = 0
blinked = True
counter_last = 0

def blink(pin):
	GPIO.output(LED, not GPIO.input(LED))
	global counter
	global blinked

	counter += 1

	if counter >=10:
		blinked = False

GPIO.add_event_detect(BTN, GPIO.RISING, blink, bouncetime = 500)

try:
	while blinked:
		if counter_last != counter:
			print(counter)
			counter_last = counter
finally:
	GPIO.output(LED, GPIO.LOW)
	GPIO.cleanup()
	print('Exit')
