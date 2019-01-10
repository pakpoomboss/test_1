from sysfs.gpio import Controller, OUTPUT, INPUT, RISING

Controller.available_pins = [37, 186]
Vibra_pin = Controller.alloc_pin(37, OUTPUT)
Button_pin = Controller.alloc_pin(186, INPUT)
Vibra_pin.set()

while 1:
	while Button_pin.read() == 0:
		Vibra_pin.reset()
	Vibra_pin.set()
