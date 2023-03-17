# Jason (Piper's Counterpart)

# Mouse Button Mapper for UNIX-based systems

This code was written to switch what extra programmable mouse buttons do in context with what the active program is, but without any hardware profiles. Kind of like what Logitech GHUB does but for UNIX based systems.

## Prerequisites

* `gi`
* `json`
* `evdev`
* `threading`

Make sure you have installed these libraries before running the code.

## Usage

1. Connect the keyboard and mouse to the system. (python find_devices.py)
2. Modify the `keyMaps.json` file to map the keys for each device and application.
3. Run the Python code. (python main.py)

## Key Mapping

Key mappings are defined in `keyMaps.json` file. This file should contain a JSON object, where the keys are device names and the values are JSON objects. Each value JSON object should have application names as keys and the values should be JSON objects that define key mappings for that device and application. For example:

```json
{
  "Logitech G304": {
    "Google Chrome": {
      "BTN_SIDE": "KEY_F5",
      "BTN_EXTRA": "KEY_F6"
    },
    "Firefox": {
      "BTN_SIDE": "KEY_F7",
      "BTN_EXTRA": "KEY_F8"
    }
  }
}
```

