#!/usr/bin/python3
#
# (C) Kirils Solovjovs, 2020
# https://kirils.org/
#

from evdev import InputDevice, ecodes as e
import time
import dbus
import alsaaudio
import os

# TODO: shuffle buttons around
# TODO: move config strings and constants to top

class dummy:
	def Get(*args):
		return 0
	
	def Set(*args):
		return None
	
	
def player_call(fun=None,arg=None):
	try:
		if fun is None:
			return dbus.Interface(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'), dbus_interface='org.freedesktop.DBus.Properties')
		else:
			if arg is None:
				return getattr(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'),fun)(dbus_interface='org.mpris.MediaPlayer2.Player')
			else:
				return getattr(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'),fun)(arg,dbus_interface='org.mpris.MediaPlayer2.Player')
	except ValueError:
		return dummy()

def set_rate(rate):
	r1=player_call().Get('org.mpris.MediaPlayer2.Player', 'MinimumRate')
	r2=player_call().Get('org.mpris.MediaPlayer2.Player', 'MaximumRate')
	rc=player_call().Get('org.mpris.MediaPlayer2.Player', 'Rate')
	if r1==r2:
		return False
		
	if rate==0:
		setpoint=1.0
	else:
		setpoint=rc+rate
	
	setpoint=round(setpoint,1)
	setpoint=min(r2,max(r1,setpoint))
	player_call().Set('org.mpris.MediaPlayer2.Player', 'Rate',setpoint)
	
	
def set_volume(vol,master_mixer):
	global last_vol
	if master_mixer:
		cur_vol = mixer.getvolume()
		cur_vol = sum(cur_vol) / len(cur_vol)
		cur_mute = any(mixer.getmute())
		if vol==0:
			mixer.setmute(not cur_mute)
		else:
			setpoint= max(min(int(cur_vol + vol*100),100),0)
			mixer.setvolume(setpoint)
	else:
		cur_vol=player_call().Get('org.mpris.MediaPlayer2.Player', 'Volume')
		if vol==0.0:
			if(cur_vol==0.0):
				vol = last_vol
			last_vol=cur_vol
			player_call().Set('org.mpris.MediaPlayer2.Player', 'Volume',vol)
		else:
			setpoint= max(min(cur_vol + vol,1.95),0)
			player_call().Set('org.mpris.MediaPlayer2.Player', 'Volume',setpoint)
	
	
	
	
	
def select_service(delta=0):
	global service,service_index,loop,shuffle
	services=[x for x in bus.list_names() if x.startswith('org.mpris.MediaPlayer2.')]
	if not len(services):
		service=""
		return False
	
	try:
		service_index=services.index(service)
	except:
		pass
	
	service_index += delta
	service_index = service_index % len(services)
	service = services[service_index]
	
	loop=player_call().Get('org.mpris.MediaPlayer2.Player', 'LoopStatus')
	try:
		loop=looptypes.index(loop)
	except:
		loop=0
	
	shuffle=player_call().Get('org.mpris.MediaPlayer2.Player', 'Shuffle') != 0
	
	return True
	

while True:
	device = None
	bus = dbus.SessionBus()
	last_vol=1.0
	mixer = alsaaudio.Mixer()
	service_index=0	
	service = ""
	
	looptypes=["None","Track","Playlist"]
	loop = 0
	shuffle = 0
	try:
		device = InputDevice("/dev/input/by-id/usb-SEM_HCT_Keyboard-event-kbd") # spec numpad
	except FileNotFoundError:
		print("not connected")
	except PermissionError:
		print("needs root")
	except:
		print("some other error")

	if not device:
		time.sleep(30)
		continue
	
	print("found device")
	for led in range(0,50):
		device.set_led(e.LED_NUML, not led % 10)
		time.sleep(0.1)
	
	device.set_led(e.LED_NUML,1)
	device.grab()
	
	
	#while not select_service():
	#	time.sleep(5)

	
	print("device ready")
	
	# TODO: define constats for readability?
	
	#   MAPPING
	# xx xx 15 xx
	# 69 98 55 14
	# 71 72 73 74
	# 75 76 77 78
	# 79[80]81 96
	# 82[57]83 96
	try:
		for event in device.read_loop():
			
			if event.type == e.EV_KEY:
				if event.value == 1 or event.value == 2: #key_down or key_repeat
					

					if event.code == 15:
						os.system("rhythmbox & ")
						continue


					if event.code == 14:
						set_volume(0.0,0 in device.leds())
						continue
						
					if event.code == 74: #swap these later
						set_volume(-0.025,0 in device.leds())
						continue
						
					if event.code == 78: #swap these later
						set_volume(+0.025,0 in device.leds())
						continue

			
					if event.code == 69: # control master system (volume)
						device.set_led(e.LED_NUML,0 not in device.leds())
						continue

						
					if not service in bus.list_names(): #service is gone
						if not select_service(): #select a different service
							break # goto sleep if not possible

											
					if event.code == 77:
						player_call('Next')
					if event.code == 76:
						player_call('Stop')
					if event.code == 75:
						player_call('Previous')
					if event.code == 96:
						player_call('PlayPause')
#					if event.code == 57:
#						player_call('Play')

						
					if event.code == 79:
						player_call('Seek',-1000000) # 1 sec
					if event.code == 81:
						player_call('Seek',+1000000) # 1 sec
						
					if event.code == 98: #loop
						loop = (loop + 1) % len(looptypes)
						player_call().Set('org.mpris.MediaPlayer2.Player', 'LoopStatus',looptypes[loop] )
						
					if event.code == 55: #shuffle
						shuffle = not shuffle
						player_call().Set('org.mpris.MediaPlayer2.Player', 'Shuffle',shuffle)
					
					if event.code == 71:
						set_rate(-0.1)
					if event.code == 73:
						set_rate(+0.1)
					if event.code == 72:
						set_rate(0)
						
					if event.code == 82:
						select_service(-1)

					if event.code == 83:
						select_service(+1)

					
					
	except OSError:
		print("device is gone")
		continue
	except:
		print("i'm a daemon. stubbornly refusing to die")

done
