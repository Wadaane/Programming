import subprocess
import sys

proc = subprocess.Popen(["python", "saymyname.py"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)

proc.stdin.write("mohamed\n")
proc.stdin.write("salim\n")
proc.stdin.write("wadaane\n")
proc.stdin.close()

while proc.returncode is None:
    proc.poll()

print "I got back from the program this:\n{0}".format(proc.stdout.read())
