import RPi.GPIO as GPIO
import time
import subprocess
import sys

led = 36
inp = 32
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led,GPIO.OUT, initial=True)
GPIO.setup(inp,GPIO.IN)

switched=False
counter=0
p = subprocess.Popen("sudo python /home/pi/SharedFolder/lcd.py ", shell=True, stdin=subprocess.PIPE) #exec 

try:
    while True:
        if GPIO.input(inp):
            if not switched:
                GPIO.output(led,not GPIO.input(led))
                
                if GPIO.input(led):
                    p.stdin.write("on\n")
                else:
                    p.stdin.write("off\n")
                time.sleep(0.2)
                switched=True
                counter+=1				
        else:
            switched =False			
        if counter>=10 :
            time.sleep(1)
            break
finally:
    p.stdin.write("exit\n")
    p.stdin.close()
    p.wait()
    #p.terminate()
    GPIO.output(led,False)
    GPIO.cleanup()
