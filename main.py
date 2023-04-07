import gi
import json
import evdev
import threading

gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Wnck

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
mouse=None
keyboard=None
kb=None
ms=None
terminateFlag=False

def findDevices():
	global keyboard
	global mouse
	global kb
	global ms
	count=0
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
		if(count==2):
					break
	kb=evdev.UInput.from_device(keyboard)
	ms=evdev.UInput.from_device(mouse)

keyMaps = json.load(open('/mnt/sda1/GitHub/Jason/keyMaps.json'))
currWindow = None

def refreshKeymaps():
	global keyMaps
	keyMaps = json.load(open('/mnt/sda1/GitHub/Jason/keyMaps.json'))

def onWindowChange(screen, prevScreen):
	global currWindow
	try:
		print(screen.get_active_window().get_name())
		for key in keyMaps[mouse.name].keys():
			if key in screen.get_active_window().get_name():
				currWindow = key
				return
		currWindow = None
	except AttributeError:
		currWindow = None
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
	global currWindow
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
				if currWindow is not None:
					print(event)
					# covert event code to key
					temp = evdev.categorize(event)
					print(temp.keycode)
					# if temp.heycode is an array
					if isinstance(temp.keycode, list):
						aSet = set(temp.keycode)
						bSet = set(keyMaps[mouse.name][currWindow].keys())
						# find intersection
						isect = aSet.intersection(bSet)
						if len(isect) > 0:
							print("A");
							# rempap to keyMaps[mouse.name][currWindow][isect[0]] on kb
							# check if mapped value is an array
							if isinstance(keyMaps[mouse.name][currWindow][isect[0]], list):
								print("B");
								for key in keyMaps[mouse.name][currWindow][isect[0]]:
									print(key)
									finalKey = getattr(evdev.ecodes, key)
									if event.value == 1:
										kb.write(evdev.ecodes.EV_KEY, finalKey, 1)
									else:
										kb.write(evdev.ecodes.EV_KEY, finalKey, 0)
								kb.syn()
							else:
								# parsing to keycode
								finalKey = getattr(evdev.ecodes, keyMaps[mouse.name][currWindow][isect[0]])
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
						if temp.keycode in keyMaps[mouse.name][currWindow].keys():
							# check if  mapped value is an array
							if isinstance(keyMaps[mouse.name][currWindow][temp.keycode], list):
								print("A2")
								for key in keyMaps[mouse.name][currWindow][temp.keycode]:
									print(key)
									finalKey = getattr(evdev.ecodes, key)
									if event.value == 1:
										kb.write(evdev.ecodes.EV_KEY, finalKey, 1)
									else:
										kb.write(evdev.ecodes.EV_KEY, finalKey, 0)
								kb.syn()
							else:
								finalKey = getattr(evdev.ecodes, keyMaps[mouse.name][currWindow][temp.keycode])
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
	except Exception as e:
		print(e)
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
				findDevices()
	return 0;

findDevices()
mouse_thread = threading.Thread(target=readMouse)
keyboard_thread = threading.Thread(target=readKeyboard)
mouse_thread.start()
keyboard_thread.start()
Gtk.main()