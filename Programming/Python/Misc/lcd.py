#!/usr/bin/env python

import time
import subprocess
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO1
import sys
import re

try:
	print('Started')

	# Raspberry Pi pin configuration:
	lcd_rs        = 21   # Note this might need to be changed to 21 for older revision Pi's.
	lcd_en        = 20
	lcd_d4        = 26
	lcd_d5        = 19
	lcd_d6        = 13
	lcd_d7        = 6
	lcd_backlight = 5

	# Define LCD column and row size for 16x2 LCD.
	lcd_columns = 16
	lcd_rows    = 2

	# Initialize the LCD using the pins above.
	lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
        	                   lcd_columns, lcd_rows, lcd_backlight)
	time.sleep(1)
	msg1 = 'a'
	msg2 = 'b'
	ip_e_found = False
	ip_w_found = False
	ip_time = 0
	t = True

	cmd1 = "ip addr show eth0 | grep inet"
	cmd2 = "ip addr show wlan0 | grep inet"

	lcd.message("   Raspberry    \n       Pi       ")

	time.sleep(1)

	# LED and Switch configuration
	led = 16 #36
	inp = 12 #32
	#GPIO.setwarnings(False)
	GPIO1.setmode(GPIO1.BCM)
	GPIO1.setup(led,GPIO1.OUT, initial=True)
	GPIO1.setup(inp,GPIO1.IN, pull_up_down = GPIO1.PUD_DOWN)

	switched=False
	counter=0

	time.sleep(1)
	
	while t:
		
		if GPIO1.input(inp):
			print('Pressed: '+str(counter))
#			if not switched:
#				GPIO1.output(led,not GPIO1.input(led))

#				if GPIO1.input(led):
#					lcd.set_backlight(1)
#				else:
#					lcd.set_backlight(0)
				#time.sleep(0.2)
#				switched=True
#				counter+=1				
#		else:
#			switched =False			
#		if counter>=5 :
#			time.sleep(1)
			t=False
			break
	
		if not ip_e_found:		
			output = subprocess.check_output(cmd1, shell=True)
			msg1 = output[9:22]
			if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', msg1) != None:
				ip_e_found = True
				ip_time = time.time()
			else:
				msg1='Connecting ...'
	
		if not ip_w_found:		
			output = subprocess.check_output(cmd2, shell=True)
			msg2 = output[9:22]
			if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', msg2) != None:
				ip_w_found = True
				ip_time = time.time()
			else:
				msg2='Connecting ...'
		lcd.clear()
		lcd.message('e:%s\nw:%s' %(msg1,msg2))

		#if (ip_e_found or ip_w_found) and time.time()>=ip_time+10:
		#	break
		
		'''for code in iter(sys.stdin.readline,''):
			code = code[:-1]
			if code == 'on':
				lcd.set_backlight(1)
				break
			elif code == 'off':
				lcd.set_backlight(0)
				break
			elif code == 'exit':
				t = False
				break'''
		time.sleep(1)		
finally:
	lcd.set_backlight(0)
	lcd.enable_display(0)
	GPIO1.output(led, False)
	GPIO1.cleanup()
