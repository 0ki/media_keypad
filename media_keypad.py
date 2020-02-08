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

# TODO: move config strings and constants to top

class dummy:
	def Get(*args):
		return 0
	
	def Set(*args):
		return None


class key:	
	at =[ #1x 2x 3x 4x
		[],
		[0,00,00,15,00], #x1
		[0,69,98,55,14], #x2
		[0,71,72,73,74], #x3
		[0,75,76,77,78], #x4
		[0,79,80,81,96], #x5 
		[0,82,57,83,96], #x6	
	]


def player_call(fun=None,arg=None):
	try:
		if fun is None:
			return dbus.Interface(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'), dbus_interface='org.freedesktop.DBus.Properties')
		else:
			if arg is None:
				return getattr(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'),fun)(dbus_interface='org.mpris.MediaPlayer2.Player')
			else:
				return getattr(dbus.SessionBus().get_object(service,'/org/mpris/MediaPlayer2'),fun)(arg,dbus_interface='org.mpris.MediaPlayer2.Player')
	except:
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
	

device = None
bus = dbus.SessionBus()
last_vol=1.0
mixer = alsaaudio.Mixer()
service_index=0	
service = ""

looptypes=["None","Track","Playlist"]
loop = 0
shuffle = 0

while True:
	
	if not device:
		try:
			device = InputDevice("/dev/input/by-id/usb-SEM_HCT_Keyboard-event-kbd") # spec numpad
		except FileNotFoundError:
			print("not connected")
		except PermissionError:
			print("needs root")
		except:
			print("some other error")

		if not device:
			time.sleep(10)
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
	
	try:
		for event in device.read_loop():
			
			if event.type == e.EV_KEY:
				if event.value == 1 or event.value == 2: #key_down or key_repeat


					if event.code == key.at[1][3]:
						os.system("rhythmbox & ")
						continue


					if event.code == key.at[4][4]:
						set_volume(0.0,0 in device.leds())
						continue
						
					if event.code == key.at[3][4]:
						set_volume(-0.025,0 in device.leds())
						continue
						
					if event.code == key.at[2][4]:
						set_volume(+0.025,0 in device.leds())
						continue

			
					if event.code == key.at[2][1]: # control master system (volume)
						device.set_led(e.LED_NUML,0 not in device.leds())
						continue

					if not service in bus.list_names(): #service is gone
						if not select_service(): #select a different service
							break # goto sleep if not possible

											
					if event.code == key.at[6][3]:
						player_call('Next')
					if event.code == key.at[6][2]:
						player_call('Stop')
					if event.code == key.at[6][1]:
						player_call('Previous')
					if event.code == key.at[6][4]:
						player_call('PlayPause')
#					if event.code == key.at[6][5]:
#						player_call('Play')

						
					if event.code == key.at[5][1]:
						player_call('Seek',-1000000) # 1 sec
					if event.code == key.at[5][3]:
						player_call('Seek',+1000000) # 1 sec
						
					if event.code == key.at[2][2]: #loop
						loop = (loop + 1) % len(looptypes)
						player_call().Set('org.mpris.MediaPlayer2.Player', 'LoopStatus',looptypes[loop] )
						
					if event.code == key.at[2][3]: #shuffle
						shuffle = not shuffle
						player_call().Set('org.mpris.MediaPlayer2.Player', 'Shuffle',shuffle)				

					if event.code == key.at[4][1]:
						set_rate(-0.1)
					if event.code == key.at[4][3]:
						set_rate(+0.1)
					if event.code == key.at[4][2]:
						set_rate(0)
						
					if event.code == key.at[3][1]:
						select_service(-1)

					if event.code == key.at[3][3]:
						select_service(+1)

					
					
	except OSError:
		device = None
		print("device is gone")
		continue
	except Exception as err:
		print("i'm a daemon. stubbornly refusing to die even though ",err)

done
