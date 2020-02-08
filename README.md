# media_keypad
Turn your USB numpad into a full-fledged media keypad


Current this only supports unix systems with dbus and alsa. I don't think I'll be spending time porting this, but pull requests adding support are welcome.

## Installation

1. Copy `30-media-keypad.rules` to `/etc/udev/rules.d`
1. Make sure that your user is in the group plugdev
1. Modify `media_keypad.py` according to your preferences, layout, apps
1. Add `media_keypad.py` to startup applications for your user session


## What's here

**experiments** contain alternative ways that you may try to get this to work

**icons** contain icons that you can use to mod your keypad

**kepad** contain keypad svg with precise measurments (pull requests welcome)
