import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Wnck
from pynput import mouse
from pynput.keyboard import Key, Controller, HotKey
keyboard = Controller()
# import keyMaps.json
import json
keyMaps=json.load(open('keyMaps.json'))
currKey=None

def onWindowChange(screen, prevScreen):
	global currKey
	try:
			# check if any key in keyMaps is in the current window title, if yes set currKey to that key
			for key in keyMaps.keys():
				if key in screen.get_active_window().get_name():
					currKey=key
					return
			# if currKey is not None, reset the key
			currKey=None
	except AttributeError:
			pass


# def on_click(x, y, button, pressed):
# 	global currKey
# 	print("currKey: ",currKey)
# 	if currKey is not None:
# 		for key in keyMaps[currKey]:
# 			if str(button.name) == key:
# 				print(key,button.name)
# 				# convert the key to a pynput key
# 				temp = HotKey.parse(keyMaps[currKey][key])
# 				for item in temp:
# 					if pressed:
# 						print("pressing: ",item)
# 						keyboard.press(item)
# 					else:
# 						print("releasing: ",item)
# 						keyboard.release(item)

# ...or, in a non-blocking fashion:
# listener = mouse.Listener(on_click=on_click)
# listener.start()

wnck_scr = Wnck.Screen.get_default()
wnck_scr.force_update()
wnck_scr.connect("active-window-changed", onWindowChange)

Gtk.main()
listener.join()