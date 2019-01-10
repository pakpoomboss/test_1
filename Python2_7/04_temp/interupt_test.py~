import os
import subprocess
import time


from sysfs.gpio import Controller, OUTPUT, INPUT, RISING

Controller.available_pins = [57]
Button_pin = Controller.alloc_pin(57, INPUT)

subprocess.Popen(['chromium-browser', 'www.arsenal.com', '--no-sandbox'], stdout=subprocess.PIPE)

flag = 1

while flag:
	if Button_pin.read() == 0:
		subprocess.Popen(['pkill', 'chromium'], stdout=subprocess.PIPE)
		flag = 0

print 'it is fucking work!!'

i = 0
while i < 5:
	print '...'
	i +=1

time.sleep(3)

subprocess.Popen(['chromium-browser', 'www.google.com', '--no-sandbox'], stdout=subprocess.PIPE)

flag = 1

while flag:
	if Button_pin.read() == 0:
		subprocess.Popen(['pkill', 'chromium'], stdout=subprocess.PIPE)
		flag = 0

print 'it is fucking work again!!'

i = 0
while i < 5:
	print '...'
	i +=1
