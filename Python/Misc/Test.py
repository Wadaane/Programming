
leave=False
print("Press Enter to toggle on/Off: anything else to exit")

while not leave:
	if input()=='':
		leave=0
	else:
		leave=1
	print("Press Enter to toggle on/Off: anything else to exit")
	##print(leave)

GPIO.cleanup()
