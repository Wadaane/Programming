import sys

print "What's your name?"

for name in iter(sys.stdin.readline, ''):
    name = name[:-1]
    if name is not "exit":
        print "Well how do you do {0} ?".format(name)
        print "What's your name ?"
print "Goodbye !"
