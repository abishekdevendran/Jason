import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
mouse=None
keyboard=None
count=0
for device in devices:
	print(device)
	if "Logitech G304" in device.name:
				print("Found mouse")
				mouse=device
				count+=1
	if("gpio-keys" in device.name):
				print("Found keyboard")
				keyboard=device
				count+=1
	if(count==2):
				break
if mouse is None or keyboard is None:
	print("Prerequisites not met")
	exit()
# print active keys on mouse
print(mouse.capabilities(verbose=True))
#initialize dummy uinput device
# kb=evdev.UInput.from_device(keyboard)
# ms=evdev.UInput.from_device(mouse)
# print(ms.capabilities(verbose=True))
# mouse.grab()
# # if BTN_EXTRA is pressed, send up arrow on keyboard, let every other event pass through
# for event in mouse.read_loop():
# 		if event.type==evdev.ecodes.EV_KEY:
# 				if event.code==evdev.ecodes.BTN_EXTRA:
# 					if event.value==1:
# 						kb.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, 1)
# 						kb.syn()
# 					if event.value==0:
# 						kb.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, 0)
# 						kb.syn()
# 				else:
# 						ms.write_event(event)
# 						ms.syn()
# 		else:
# 				ms.write_event(event)
# 				ms.syn()

for event in mouse.read_loop():
		if event.type==evdev.ecodes.EV_KEY:
			print(event.code)