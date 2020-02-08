#!/bin/bash
#
# (C) Kirils Solovjovs, 2020
# https://kirils.org/
#
# This is the simpler and more straight forward way, but it didn't agree
# with my window manager.

# layout
# x     x     TAB   x
# NMLK  KPDV  KPMU  BKSP*
# KP7   KP8   KP9   KPSU
# KP4   KP5   KP6   KPAD
# KP1   KP2   KP3   KPEN
# KP0   SPCE  KPPT  KPEN

# See these files for constants
# /usr/include/X11/keysymdef.h
# /usr/include/X11/XF86keysym.h
# /usr/share/X11/xkb/symbols/inet


while true; do


  mediakp_id="$(xinput list |sed -n 's/.*SEM HCT Keyboard.*id=\([0-9]*\).*keyboard.*/\1/p' | head -1)"
  [ "$mediakp_id" ] || (sleep 120 && continue)

  mkdir -p /tmp/xkb/symbols


  cat >/tmp/xkb/symbols/custom <<EOF
xkb_symbols "mediakp" {
  key <KPAD> { [ XF86AudioRaiseVolume, XF86AudioRaiseVolume ] };
  key <KPSU> { [ XF86AudioLowerVolume, XF86AudioLowerVolume ] };
  key <KP6> { [ XF86AudioNext, XF86AudioNext ] };
  key <KP4> { [ XF86AudioPrev, XF86AudioPrev ] };
  key <KPEN> { [ XF86AudioMute, XF86AudioMute ] };
  key <KP5> { [ XF86AudioStop, XF86AudioStop] };
};
EOF

  setxkbmap -device $mediakp_id -print \
   | sed 's/\(xkb_symbols.*\)"/\1+custom(mediakp)"/' \
   | xkbcomp -I/tmp/xkb -i $mediakp_id -synch - $DISPLAY 2>/dev/null

  sleep 600
done
