import os
import RPi.GPIO as GPIO
import time
import re
import locale

def get_cpu_temperature():
	res = os.popen('vcgencmd measure_temp').readline()
	return re.findall("\d*\.\d*",res)[0]

class Buzzer:
	def _init_(self):
		GPIO.setmode(GPIO.BOARD)
		self.buzzer_pin = 21
		GPIO.setup(self.buzzer_pin, GPIO.IN)
		GPIO.setup(self.buzzer_pin, GPIO.OUT)
	
	def _del_(self):
		class_name = self._class_._name_

	def get_cpu_temperature(self, current_temp, kinda_hot, too_hot):
		while True:
			current_temp=get_cpu_temperature()
			#print time.ctime()
			#print current_temp
			if locale.atof(current_temp) > (too_hot):
	#
	#                     TOO HOT ALARM
	# The default setting is: 1s beep 1s silence 1s beep etc
	#
				#print time.ctime()
				#print current_temp
				GPIO.output(self.buzzer_pin, True)
				time.sleep(1)                          # beeps for 1 second
				GPIO.output(self.buzzer_pin, False)
				time.sleep(1)                          # silence for 1 second
			elif locale.atof(current_temp) > (kinda_hot):
	#
	#                    KINDA HOT ALARM
	# The default setting is: 0.25s beep 5s silence 0.25s beep etc
	#
				#print time.ctime()
				#print current_temp
				GPIO.output(self.buzzer_pin, True)
				time.sleep(0.25)                       # beeps for 0.25 seconds
				GPIO.output(self.buzzer_pin, False)
				time.sleep(5)                          # silence for 5 seconds
			else:
	#
	#                    IDLE MODE
	# To keep the CPU usage low, do not use a too low value
	# I thinkg that 10 seconds should do 
				time.sleep(10)                         # idle for 10s

				
#buzzer = Buzzer()
#buzzer.get_cpu_temperature(get_cpu_temperature(), 80.0, 85.0)

#[Desktop Entry]
#Name=OverHeatingAlarm
#Exec=python "home/pi/.oha.py"
#Type=Application