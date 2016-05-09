# This file is part of Jeedom.
#
# Jeedom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Jeedom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Jeedom. If not, see <http://www.gnu.org/licenses/>.

import logging
import requests
import pdb
import string
import sys
import os
import time
import datetime
import binascii
import traceback
import subprocess
import threading
from threading import Thread, Event, Timer
import re
import signal
import xml.dom.minidom as minidom
from optparse import OptionParser
import socket
import select
import inspect
from os.path import join
import serial

try:
	from jeedom.jeedom import *
except ImportError:
	print "Error: importing module from jeedom folder"
	sys.exit(1)

DimOff_threads = {}

def sendDimOff(action, url, trigger_timeout,dictkey):
	command = Command(url,action)
	command.run(timeout=trigger_timeout)
	del DimOff_threads[dictkey]

def decodePacket(message):
	global _prevMessage;
	global _prevDatetime;
	global _timerDatetime;
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
	unixtime_utc = int(time.time())
	unixtime_utc_check = datetime.datetime.utcnow()
	if not test_edisio( jeedom_utils.ByteToHex(message) ):
		logging.error("The incoming message is invalid (" + jeedom_utils.ByteToHex(message) + ")")
		return
	raw_message = jeedom_utils.ByteToHex(message)
	raw_message = raw_message.replace(' ', '')
	PID = jeedom_utils.ByteToHex(message[3]) + jeedom_utils.ByteToHex(message[4]) + jeedom_utils.ByteToHex(message[5]) + jeedom_utils.ByteToHex(message[6])
	BID = jeedom_utils.ByteToHex(message[7])
	MID = jeedom_utils.ByteToHex(message[8])
	BL = jeedom_utils.ByteToHex(message[9])
	RMAX = jeedom_utils.ByteToHex(message[10])
	RC = jeedom_utils.ByteToHex(message[11])
	CMD = jeedom_utils.ByteToHex(message[12])
	DATA = 'None'
	if len(message) > 16:
		DATA = ''
		for i in range(0,len(message) - 16):
			DATA += jeedom_utils.ByteToHex(message[13 + i])
	clean_message = str(PID) + str(BID) + str(MID) + str(RMAX) + str(CMD) + str(DATA)
	if CMD in ['07'] and MID in ['01']:
		if  DimOff_threads.has_key(str(PID)+str(BID)):
			if clean_message == _prevMessage and unixtime_utc_check < (_timerDatetime+datetime.timedelta(milliseconds=800)) :
				logging.debug("Too soon to refresh timer")
			else:
				logging.debug("Thread exists resetting")
				_timerDatetime = unixtime_utc_check
				dimmingOff_thread = DimOff_threads.get(str(PID)+str(BID))
				dimmingOff_thread.reset(1)
		else:
			logging.debug("Thread not exists creating")
			BLDIM = int((int(BL, 16) / 3.3) * 10)
			dimOff = {'id' : str(PID), 'battery' : str(BLDIM), 'mid' : str(MID),'apikey' : str(config.apikey)}
			dimOff['bt'] = str(BID)
			dimOff['value'] = 'down'
			dimmingOff = TimerReset(1, function=sendDimOff, args=(dimOff, config.trigger_url, config.trigger_timeout,str(PID)+str(BID)))
			DimOff_threads[str(PID)+str(BID)] = dimmingOff
			_timerDatetime = unixtime_utc_check
			dimmingOff.start()
		if clean_message == _prevMessage and unixtime_utc_check < (_prevDatetime+datetime.timedelta(milliseconds=4000)) :
			return
	else:
		if clean_message == _prevMessage and unixtime_utc_check < (_prevDatetime+datetime.timedelta(milliseconds=200)) :
			logging.debug("Message already decode, ignore")
			return
	_prevMessage = clean_message
	_prevDatetime = unixtime_utc_check
	decode_string = "\nPID\t\t\t= " + str(PID);
	decode_string += "\nBID\t\t\t= " + str(BID);
	decode_string += "\nMID\t\t\t= " + str(MID);
	decode_string += "\nBL\t\t\t= " + str(BL);
	decode_string += "\nRMAX\t\t\t= " + str(RMAX);
	decode_string += "\nRC\t\t\t= " + str(RC);
	decode_string += "\nCMD\t\t\t= " + str(CMD);
	decode_string += "\nDATA\t\t\t= " + str(DATA);
	BL = int((int(BL, 16) / 3.3) * 10)
	action = {'id' : str(PID), 'battery' : str(BL), 'mid' : str(MID)}
	key = str(PID)+str(MID)+str(CMD)+str(BID)
	value = ''

	if CMD == '01':
		decode_string += "\nCommand value : \t= ON"
		value = 1
	if CMD == '02':
		decode_string += "\nCommand value : \t= OFF"
		value = 0
	if CMD == '03':
		decode_string += "\nCommand value : \t= Toogle"
		value = 'toggle'
	if CMD == '04':
		decode_string += "\nCommand value : \t= Dim"
		value = 'toggle'
	if CMD == '05':
		decode_string += "\nCommand value : \t= Dim up"
		value = 'toggle'
	if CMD == '06':
		decode_string += "\nCommand value : \t= Dim down"
		value = 'toggle'
	if CMD == '07':
		decode_string += "\nCommand value : \t= Dim A"
		value = 'up'
	if CMD == '08':
		decode_string += "\nCommand value : \t= Dim stop"
		value = 'toggle'
	if CMD == '09':
		decode_string += "\nCommand value : \t= Shutter open"
		value = 1
	if CMD == '0A':
		decode_string += "\nCommand value : \t= Shutter close"
		value = 0
	if CMD == '0B':
		decode_string += "\nCommand value : \t= Shutter stop"
		value = 0
	if CMD == '0C':
		decode_string += "\nCommand value : \t= RGB"
		value = 0
	if CMD == '0D':
		decode_string += "\nCommand value : \t= RGB c"
		value = 0
	if CMD == '0E':
		decode_string += "\nCommand value : \t= RGB plus"
		value = 0
	if CMD == '0F':
		decode_string += "\nCommand value : \t= Open slow"
		value = 0
	if CMD == '10':
		decode_string += "\nCommand value : \t= Set short"
		value = 0
	if CMD == '11':
		decode_string += "\nCommand value : \t= Set 5s"
		value = 0
	if CMD == '12':
		decode_string += "\nCommand value : \t= Set 10s"
		value = 0
	if CMD == '13':
		decode_string += "\nCommand value : \t= Close slow"
		value = 0
	if CMD == '14':
		decode_string += "\nCommand value : \t= Dim stop2"
		value = 0
	if CMD == '15':
		decode_string += "\nCommand value : \t= Set long up"
		value = 0
	if CMD == '16':
		decode_string += "\nCommand value : \t= Study"
		value = 0
	if CMD == '17':
		decode_string += "\nCommand value : \t= Del button"
		value = 0
	if CMD == '18':
		decode_string += "\nCommand value : \t= Del all"
		value = 0
	if CMD == '19':
		decode_string += "\nCommand value : \t= Door close"
		value = 0
	if CMD == '1A':
		decode_string += "\nCommand value : \t= Door open"
		value = 1
	if CMD == '1F':
		decode_string += "\nCommand value : \t= Broadcast query"
		value = 0
	if CMD == '20':
		decode_string += "\nCommand value : \t= Querry status"
		value = 0
	if CMD == '21':
		decode_string += "\nCommand value : \t= Report status"
		value = 0
	if CMD == 'F1':
		decode_string += "\nCommand value : \t= Dim to 10%"
		value = 10
	if CMD == 'F2':
		decode_string += "\nCommand value : \t= Dim to 20%"
		value = 20
	if CMD == 'F3':
		decode_string += "\nCommand value : \t= Dim to 30%"
		value = 30
	if CMD == 'F4':
		decode_string += "\nCommand value : \t= Dim to 40%"
		value = 40
	if CMD == 'F5':
		decode_string += "\nCommand value : \t= Dim to 50%"
		value = 50
	if CMD == 'F6':
		decode_string += "\nCommand value : \t= Dim to 60%"
		value = 60
	if CMD == 'F7':
		decode_string += "\nCommand value : \t= Dim to 70%"
		value = 70
	if CMD == 'F8':
		decode_string += "\nCommand value : \t= Dim to 80%"
		value = 80
	if CMD == 'F9':
		decode_string += "\nCommand value : \t= Dim to 90%"
		value = 90
	if CMD == 'FA':
		decode_string += "\nCommand value : \t= Dim to 100%"
		value = 100

	if MID == '01':
		decode_string += "\nDecode model : \t\t= Emitter Channel 1"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '02':
		decode_string += "\nDecode model : \t\t= Emitter Channel 2"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '03':
		decode_string += "\nDecode model : \t\t= Emitter Channel 3"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '04':
		decode_string += "\nDecode model : \t\t= Emitter Channel 4"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '05':
		decode_string += "\nDecode model : \t\t= Emitter Channel 5"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '06':
		decode_string += "\nDecode model : \t\t= Energy Meter"

	if MID == '07':
		decode_string += "\nDecode model : \t\t= Motion Sensor (On/Off/Pulse)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '08':
		decode_string += "\nDecode model : \t\t= Temperature Sensor"
		try:
			temperature = float(int(DATA[3:4]+DATA[0:2],16)) / 100
		except Exception, e:
			logging.debug("Error on temperature decode "+str(e))
			return
		action['temperature'] = str(temperature)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '09':
		decode_string += "\nDecode model : \t\t= Door Sensor (On/Off/Pulse)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '10':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (On/Off/Pulse)"

	if MID == '11':
		decode_string += "\nDecode model : \t\t= Receiver 2 Outputs (On/Off or Pulse)"

	if MID == '12':
		decode_string += "\nDecode model : \t\t= Receiver 4 Outputs (On/Off or Dimer)"

	if MID == '13':
		decode_string += "\nDecode model : \t\t= Receiver 4 Outputs (On/Off/Pulse or 2x Open/Close)"

	if MID == '14':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (On/Off or Dimer)"

	if MID == '15':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (On/Off or Dimer)"

	if MID == '16':
		decode_string += "\nDecode model : \t\t= Gateway (esaylink)"

	if MID == '17':
		decode_string += "\nDecode model : \t\t= Emitter 2 Channels (Button)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '18':
		decode_string += "\nDecode model : \t\t= Emitter 2 Channels (Button)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '0B':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (On/Off)"

	if MID == '0E':
		decode_string += "\nDecode model : \t\t= Thermostat"

	if MID == '0F':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (Heater On/Off)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '0C':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (Pilot Wire Functions)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '0D':
		decode_string += "\nDecode model : \t\t= Receiver 2 Outputs (1x Open/Close)"

	if MID == '1B':
		decode_string += "\nDecode model : \t\t= IR transmitter (Trigger)"

	if MID == '1D':
		decode_string += "\nDecode model : \t\t= EMC-CAR (Trigger)"
		if CMD == '0B':
			action['state'] = '1'
		if CMD == '0A':
			action['state'] = '2'
		if CMD == '09':
			action['state'] = '3'
		jeedom_com.add_changes('devices::'+str(key),action);

	if MID == '1E':
		decode_string += "\nDecode model : \t\t= Enocean Sensor (Door)"

	if MID == '1F':
		decode_string += "\nDecode model : \t\t= Enocean Sensor (Temperature)"

	if MID == '20':
		decode_string += "\nDecode model : \t\t= Enocean Switch (Switch)"

	if MID == '21':
		decode_string += "\nDecode model : \t\t= Virtual Device (IR Remote Control)"

	if MID == '22':
		decode_string += "\nDecode model : \t\t= Enocean (Motion Sensor)"

	if MID == '23':
		decode_string += "\nDecode model : \t\t= Enocean socket"

	logging.debug("Decode packet : "+decode_string)
	return

# ----------------------------------------------------------------------------

def test_edisio( message ):
	# Remove all invalid characters
	message = jeedom_utils.stripped(message)
	
	# Remove any whitespaces
	try:
		message = message.replace(' ', '')
	except Exception:
		logging.debug("Error: Removing white spaces")
		return False
	
	# Test the string if it is hex format
	try:
		int(message,16)
	except Exception:
		logging.debug("Error: Packet not hex format")
		return False
	
	# Check that length is even
	if len(message) % 2:
		logging.debug("Error: Packet length not even")
		return False

	if len(message.decode('hex')) < 16:
		logging.debug("Error: Packet length is not valid (<16)")
		return False
	
	# Check that first byte is not 6C
	if jeedom_utils.ByteToHex(message.decode('hex')[0]) <> "6C":
		logging.debug("Error: Packet first byte is not 6C : "+str(jeedom_utils.ByteToHex(message.decode('hex')[0])))
		return False

	if jeedom_utils.ByteToHex(message.decode('hex')[1]) <> "76":
		logging.debug("Error: Packet second byte is not 76 : "+str(jeedom_utils.ByteToHex(message.decode('hex')[0])))
		return False

	if jeedom_utils.ByteToHex(message.decode('hex')[2]) <> "63":
		logging.debug("Error: Packet third byte is not 63 : "+str(jeedom_utils.ByteToHex(message.decode('hex')[0])))
		return False

	if jeedom_utils.ByteToHex(message.decode('hex')[-1]) <> "0A":
		logging.debug("Error: Packet last byte is not 0A : "+str(jeedom_utils.ByteToHex(message.decode('hex')[-1])))
		return False

	if jeedom_utils.ByteToHex(message.decode('hex')[-2]) <> "0D":
		logging.debug("Error: Packet -2 byte is not 0D : "+str(jeedom_utils.ByteToHex(message.decode('hex')[-2])))
		return False

	if jeedom_utils.ByteToHex(message.decode('hex')[-3]) <> "64":
		logging.debug("Error: Packet -3 byte is not 64 : "+str(jeedom_utils.ByteToHex(message.decode('hex')[-3])))
		return False
	
	# Length more than one byte
	if not len(message.decode('hex')) > 1:
		logging.debug("Error: Packet is not longer than one byte")
		return False

	return True
			
# ----------------------------------------------------------------------------

def read_edisio():
	message = None
	byte = jeedom_serial.read()
	try:
		if str(jeedom_utils.ByteToHex(byte)) == '6C' :
			message = byte + jeedom_serial.readbytes(15)
			if str(jeedom_utils.ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += jeedom_serial.readbytes(1)
			if str(jeedom_utils.ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += jeedom_serial.readbytes(1)
			if str(jeedom_utils.ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += jeedom_serial.readbytes(1)
			if str(jeedom_utils.ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += jeedom_serial.readbytes(1)
			logging.debug("Message: " + str(jeedom_utils.ByteToHex(message)))
			decodePacket(message);
	except OSError, e:
		logging.error("Traceback: " + traceback.format_exc())
		logging.error("------------------------------------------------")
		logging.error("Received\t\t= " + jeedom_utils.ByteToHex(message))

# ----------------------------------------------------------------------------

def listen():
	logging.debug("Start listening...")
	jeedom_serial.open()
	jeedom_socket.open()
	try:
		while 1:
			time.sleep(0.02)
			rawcmd = read_edisio()
			if rawcmd:
				logging.debug("Processed: " + str(rawcmd))
			read_socket()
	except KeyboardInterrupt:
		logging.debug("Received keyboard interrupt")
		logging.debug("Close server socket")
		serversocket.netAdapter.shutdown()
		logging.debug("Close serial port")
		jeedom_serial.close()
		pass

# ----------------------------------------------------------------------------
	
def read_socket():
	global JEEDOM_SOCKET_MESSAGE
	if not JEEDOM_SOCKET_MESSAGE.empty():
		logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
		message = jeedom_utils.stripped(JEEDOM_SOCKET_MESSAGE.get())
		if test_edisio( message ):
			logging.debug("------------------------------------------------")
			logging.debug("Incoming message from socket")
			logging.debug("Send\t\t\t= " + jeedom_utils.ByteToHex(message.decode('hex')))
			logging.debug("Packet Length\t\t= " + jeedom_utils.ByteToHex(message.decode('hex')[0]))
			logging.debug("Write message to serial port : " + jeedom_utils.ByteToHex( message.decode('hex')))
			jeedom_serial.write( message.decode('hex'))
			logging.debug("Write 1")
			time.sleep(0.14)
			jeedom_serial.write( message.decode('hex'))
			logging.debug("Write 2")
			time.sleep(0.14)
			jeedom_serial.write( message.decode('hex'))
			logging.debug("Write 3")
		else:
			logging.error("Invalid message from socket : " + str(message))

# ----------------------------------------------------------------------------

def handler(signum=None, frame=None):
	logging.debug("Signal %i caught, exiting..." % int(signum))
	shutdown()

def shutdown():
	logging.debug("Shutdown")
	logging.debug("Removing PID file " + str(_pidfile))
	try:
		os.remove(_pidfile)
	except:
		pass
	try:
		jeedom_socket.close()
	except:
		pass
	try:
		jeedom_serial.close()
	except:
		pass
	logging.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)

# ----------------------------------------------------------------------------

_log_level = "Error"
_socket_port = 55005
_socket_host = 'localhost'
_device = 'auto'
_pidfile = '/tmp/edisio.pid'
_apikey = ''
_callback = ''
_serial_rate = 9600
_serial_timeout = 9
_cycle = 0.5;
_prevMessage = '';
_prevDatetime = datetime.datetime.utcnow();
_timerDatetime = datetime.datetime.utcnow();

for arg in sys.argv:
	if arg.startswith("--loglevel="):
		temp, _log_level = arg.split("=")
		jeedom_utils.set_log_level(_log_level)
	elif arg.startswith("--socketport="):
		temp, _socket_port = arg.split("=")
	elif arg.startswith("--sockethost="):
		temp, _socket_host = arg.split("=")
	elif arg.startswith("--pidfile="):
		temp, _pidfile = arg.split("=")
	elif arg.startswith("--device="):
		temp, _device = arg.split("=")
	elif arg.startswith("--apikey="):
		temp, _apikey = arg.split("=")
	elif arg.startswith("--callback="):
		temp, _callback = arg.split("=")
	elif arg.startswith("--cycle="):
		temp, _cycle = arg.split("=")

_socket_port = int(_socket_port)
_cycle = float(_cycle)

logging.info('Start edisiocmd')
logging.info('Log level : '+str(_log_level))
logging.info('Socket port : '+str(_socket_port))
logging.info('Socket host : '+str(_socket_host))
logging.info('PID file : '+str(_pidfile))
logging.info('Device : '+str(_device))
logging.info('Apikey : '+str(_apikey))
logging.info('Callback : '+str(_callback))
logging.info('Cycle : '+str(_cycle))
logging.info('Serial rate : '+str(_serial_rate))
logging.info('Serial timeout : '+str(_serial_timeout))

if _device == 'auto':
	_device = jeedom_utils.find_tty_usb('067b','2303')
	logging.info('Find device : '+str(_device))

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)	

try:
	jeedom_utils.wrtie_pid(str(_pidfile))
	jeedom_com = jeedom_com(apikey = _apikey,url = _callback,cycle=_cycle)
	jeedom_serial = jeedom_serial(device=_device,rate=_serial_rate,timeout=_serial_timeout)
	jeedom_socket = jeedom_socket(port=_socket_port,address=_socket_host)
	listen()
except Exception,e:
	logging.error('Fatal error : '+str(e))
	shutdown()