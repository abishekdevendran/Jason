import gi
import json
import evdev
import threading

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
mouse=None
keyboard=None
count=0
terminateFlag=False

for device in devices:
	if "Logitech G304" == device.name:
				print("Found mouse")
				print(device)
				mouse=device
				count+=1
	if("Dell KB216 Wired Keyboard" == device.name):
				print("Found keyboard")
				print(device)
				keyboard=device
				count+=1
	# if(count==2):
	# 			break
if mouse is None or keyboard is None:
	print("Prerequisites not met")
	exit()

kb=evdev.UInput.from_device(keyboard)
ms=evdev.UInput.from_device(mouse)

gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Wnck

keyMaps = json.load(open('/mnt/sda1/GitHub/Jason/keyMaps.json'))
currKey = None

def refreshKeymaps():
	global keyMaps
	keyMaps = json.load(open('/mnt/sda1/GitHub/Jason/keyMaps.json'))

def onWindowChange(screen, prevScreen):
	global currKey
	try:
		print(screen.get_active_window().get_name())
		for key in keyMaps[mouse.name].keys():
			if key in screen.get_active_window().get_name():
				currKey = key
				return
		currKey = None
	except AttributeError:
		currKey = None
		pass
#attach callback to screen
screen = Wnck.Screen.get_default()
screen.connect("active-window-changed", onWindowChange)
screen.force_update()

def is_valid_ecode(key_name):
		try:
				getattr(evdev.ecodes, key_name)
				return True
		except AttributeError:
				return False

def validate_key_maps(json_obj):
		for device_name, key_maps in json_obj.items():
				for app_name, keys in key_maps.items():
						for key_name, value in keys.items():
								if not is_valid_ecode(key_name):
										print(f"Invalid key name '{key_name}' in key map for app '{app_name}' and device '{device_name}'")
										exit()
								if isinstance(value, str) and not is_valid_ecode(value):
										print(f"Invalid value '{value}' in key map for key '{key_name}', app '{app_name}', and device '{device_name}'")
										exit()
		return None

validate_key_maps(keyMaps)

def readMouse():
	global currKey
	global ms
	global kb
	global mouse
	global terminateFlag
	mouse.grab()
	try:
		for event in mouse.read_loop():
			if terminateFlag:
				break
			if event.type==evdev.ecodes.EV_KEY:
				#if key is being held, do nothing
				if event.value==2:
					continue
				# check if key is mapped
				if currKey is not None:
					print(event)
					# covert event code to key
					temp = evdev.categorize(event)
					print(temp.keycode)
					# if temp.heycode is an array
					if isinstance(temp.keycode, list):
						aSet = set(temp.keycode)
						bSet = set(keyMaps[mouse.name][currKey].keys())
						# find intersection
						isect = aSet.intersection(bSet)
						if len(isect) > 0:
							# rempap to keyMaps[mouse.name][currKey][isect[0]] on kb
							# parsing to keycode
							finalKey = getattr(evdev.ecodes, keyMaps[mouse.name][currKey][isect[0]])
							if event.value == 1:
								kb.write(evdev.ecodes.EV_KEY, finalKey, 1)
								kb.syn()
							else:
								kb.write(evdev.ecodes.EV_KEY, finalKey, 0)
								kb.syn()
						else:
							ms.write(event.type, event.code, event.value)
							ms.syn()
					else:
						# check if key is mapped
						if temp.keycode in keyMaps[mouse.name][currKey].keys():
							finalKey = getattr(evdev.ecodes, keyMaps[mouse.name][currKey][temp.keycode])
							if event.value == 1:
								kb.write(evdev.ecodes.EV_KEY, finalKey, 1)
								kb.syn()
							else:
								kb.write(evdev.ecodes.EV_KEY, finalKey, 0)
								kb.syn()
						else:
							ms.write(event.type, event.code, event.value)
							ms.syn()
				else:
					ms.write(event.type, event.code, event.value)
					ms.syn()
			else:
				ms.write(event.type, event.code, event.value)
				ms.syn()
	except:
		print("Mouse disconnected")
	finally:
		mouse.ungrab()
		ms.close()
		kb.close()
		Gtk.main_quit()
	return 0

def readKeyboard(): 
	hotkey=["KEY_LEFTCTRL","KEY_LEFTALT","KEY_LEFTSHIFT","KEY_Q"]
	refresh=["KEY_LEFTCTRL","KEY_LEFTALT","KEY_LEFTSHIFT","KEY_R"]
	global keyboard
	global terminateFlag
	# check for a specific comination being held down: cltr+alt+shift+q
	def mapper(keystr):
		return getattr(evdev.ecodes, keystr)
	hotkey = map(mapper, hotkey)
	refresh = map(mapper, refresh)
	setA = set(hotkey)
	setB = set(refresh)
	print(setA, setB)
	# if so, set terminateFlag to true
	for event in keyboard.read_loop():
		if event.type == evdev.ecodes.EV_KEY:
			if event.value == 2:
				continue
			# check if keyboard.active_keys() array has same elements as hotkey
			temp = set(keyboard.active_keys())
			print(temp, setB)
			if setA.intersection(temp) == setA:
				print("Exiting")
				terminateFlag = True
				break
			elif setB.intersection(temp) == setB:
				print("Refreshing")
				refreshKeymaps()
	return 0;

mouse_thread = threading.Thread(target=readMouse)
keyboard_thread = threading.Thread(target=readKeyboard)
mouse_thread.start()
keyboard_thread.start()
Gtk.main()