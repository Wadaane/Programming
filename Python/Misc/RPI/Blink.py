import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.OUT)

leave=False
print("Press Enter to toggle on/Off: anything else to exit")

while(not leave):
	GPIO.output(3,GPIO.input(3)^1)
	if input()=='':
		leave=0
	else:
		leave=1
	print("Press Enter to toggle on/Off: anything else to exit")

GPIO.cleanup()