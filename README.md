# media_keypad
Turn your USB numpad into a full-fledged media (or other custom) keypad.

![Design](/design.png) ![Finished device](/product.jpg)

**Q**: How is this better than multimedia keys I have on my out-of-the-box keyboard?

**A**: This method:
* is a separate sattelite controller
* has way more keys, e.g. adjustment of playback speed
* allows to control volume of each app (even the background ones) seperately
* allows for custom actions
* works even with computer locked
* is not seen as keyboard input by the OS, so does not disturb your use of other keyboard or mouse

Current this only supports unix systems with dbus and alsa. I don't think I'll be spending time porting this, but pull requests adding support for additional operating systems are welcome.

## Installation

1. `sudo apt-get install libasound2-dev` (debian)
1. `sudo apt-get install python3-evdev` (debian)
1. `python3 -m pip install pyalsaaudio `
1. Copy `30-media-keypad.rules` to `/etc/udev/rules.d`
1. Make sure that your user is in the group `plugdev`
1. Modify `media_keypad.py` according to your preferences, layout, apps
1. Add `media_keypad.py` to startup applications for your user session


## What's where

**experiments** contain alternative ways that you may try to get this to work

**icons** contain icons that you can use to mod your keypad

**kepad** contain keypad svg with precise measurments (pull requests welcome)
