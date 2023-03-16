import gi
import json
import evdev
import threading

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
mouse=None
keyboard=None
count=0
for device in devices:
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

kb=evdev.UInput.from_device(keyboard)
ms=evdev.UInput.from_device(mouse)

gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, GLib, Wnck

keyMaps = json.load(open('keyMaps.json'))
currKey = None

def onWindowChange(screen, prevScreen):
    global currKey
    if(screen.get_active_window() is None):
        return
    print(screen.get_active_window().get_name())
    try:
        for key in keyMaps.keys():
            if key in screen.get_active_window().get_name():
                currKey = key
                return
        currKey = None
    except AttributeError:
        pass
#attach callback to screen
screen = Wnck.Screen.get_default()
screen.connect("active-window-changed", onWindowChange)
screen.force_update()

def readMouse():
    mouse.grab()
    for event in mouse.read_loop():
        if event.type==evdev.ecodes.EV_KEY:
            if event.code==evdev.ecodes.BTN_EXTRA and event.value==1:
                kb.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, 1)
                kb.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, 0)
                kb.syn()
            else:
                ms.write_event(event)
                ms.syn()
        else:
            ms.write_event(event)
            ms.syn()
    return True

mouse_thread = threading.Thread(target=readMouse)
mouse_thread.start()
Gtk.main()