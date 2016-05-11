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
import string
import sys
import os
import time
import datetime
import binascii
import threading
from threading import Thread, Event, Timer
import re
import signal
from optparse import OptionParser
from os.path import join
import json

try:
	from jeedom.jeedom import *
except ImportError:
	print "Error: importing module from jeedom folder"
	sys.exit(1)
	
def TimerReset(*args, **kwargs):
    """ Global function for Timer """
    return _TimerReset(*args, **kwargs)


class _TimerReset(Thread):
    """Call a function after a specified number of seconds:
    t = TimerReset(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.resetted = True

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        logging.debug("Time: %s - timer running..." % time.asctime())

        while self.resetted:
            logging.debug("Time: %s - timer waiting for timeout in %.2f..." % (time.asctime(), self.interval))
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        logging.debug("Time: %s - timer finished!" % time.asctime())

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            logging.debug("Time: %s - timer resetting to %.2f..." % (time.asctime(), interval))
            self.interval = interval
        else:
            logging.debug("Time: %s - timer resetting..." % time.asctime())

        self.resetted = True
        self.finished.set()
        self.finished.clear()
		
DimOff_threads = {}

def sendDimOff(key,action):
	jeedom_com.add_changes('devices::'+key,action)
	del DimOff_threads[key]

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
			dimOff = {'id' : str(PID), 'battery' : str(BLDIM), 'mid' : str(MID)}
			dimOff['bt'] = str(BID)
			dimOff['value'] = 'down'
			dimmingOff = TimerReset(1, function=sendDimOff, args=(str(PID)+str(BID),dimOff))
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
	BL = int((int(BL, 16) / 3.3) * 10)
	action = {'id' : str(PID), 'battery' : str(BL), 'mid' : str(MID)}
	key = str(PID)+str(MID)+str(CMD)+str(BID)
	value = ''

	if CMD == '01':
		value = 1
	if CMD == '02':
		value = 0
	if CMD == '03':
		value = 'toggle'
	if CMD == '04':
		value = 'toggle'
	if CMD == '05':
		value = 'toggle'
	if CMD == '06':
		value = 'toggle'
	if CMD == '07':
		value = 'up'
	if CMD == '08':
		value = 'toggle'
	if CMD == '09':
		value = 1
	if CMD == '0A':
		value = 0
	if CMD == '0B':
		value = 0
	if CMD == '0C':
		value = 0
	if CMD == '0D':
		value = 0
	if CMD == '0E':
		value = 0
	if CMD == '0F':
		value = 0
	if CMD == '10':
		value = 0
	if CMD == '11':
		value = 0
	if CMD == '12':
		value = 0
	if CMD == '13':
		value = 0
	if CMD == '14':
		value = 0
	if CMD == '15':
		value = 0
	if CMD == '16':
		value = 0
	if CMD == '17':
		value = 0
	if CMD == '18':
		value = 0
	if CMD == '19':
		value = 0
	if CMD == '1A':
		value = 1
	if CMD == '1F':
		value = 0
	if CMD == '20':
		value = 0
	if CMD == '21':
		value = 0
	if CMD == 'F1':
		value = 10
	if CMD == 'F2':
		value = 20
	if CMD == 'F3':
		value = 30
	if CMD == 'F4':
		value = 40
	if CMD == 'F5':
		value = 50
	if CMD == 'F6':
		value = 60
	if CMD == 'F7':
		value = 70
	if CMD == 'F8':
		value = 80
	if CMD == 'F9':
		value = 90
	if CMD == 'FA':
		value = 100

	if MID == '01':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '02':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '03':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '04':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '05':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '06':
		return
	if MID == '07':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '08':
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
		return
	if MID == '11':
		return
	if MID == '12':
		return
	if MID == '13':
		return
	if MID == '14':
		return
	if MID == '15':
		return
	if MID == '16':
		return
	if MID == '17':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '18':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '0B':
		return
	if MID == '0E':
		return
	if MID == '0F':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '0C':
		action['bt'] = str(BID)
		action['value'] = str(value)
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '0D':
		return
	if MID == '1B':
		return
	if MID == '1D':
		if CMD == '0B':
			action['state'] = '1'
		if CMD == '0A':
			action['state'] = '2'
		if CMD == '09':
			action['state'] = '3'
		jeedom_com.add_changes('devices::'+str(key),action);
	if MID == '1E':
		return
	if MID == '1F':
		return
	if MID == '20':
		return
	if MID == '21':
		return
	if MID == '22':
		return
	if MID == '23':
		return
	return

# ----------------------------------------------------------------------------

def test_edisio( message ):
	message = jeedom_utils.stripped(message)
	try:
		message = message.replace(' ', '')
	except Exception:
		logging.debug("Error: Removing white spaces")
		return False
	try:
		int(message,16)
	except Exception:
		logging.debug("Error: Packet not hex format")
		return False
	if len(message) % 2:
		logging.debug("Error: Packet length not even")
		return False
	if len(message.decode('hex')) < 16:
		logging.debug("Error: Packet length is not valid (<16)")
		return False
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
		logging.error("------------------------------------------------")
		logging.error("Received\t\t= " + jeedom_utils.ByteToHex(message))

# ----------------------------------------------------------------------------

def listen():
	logging.debug("Start listening...")
	jeedom_serial.open()
	jeedom_socket.open()
	jeedom_serial.flushOutput()
	jeedom_serial.flushInput()
	try:
		while 1:
			time.sleep(0.02)
			read_edisio()
			read_socket()
	except KeyboardInterrupt:
		shutdown()

# ----------------------------------------------------------------------------
	
def read_socket():
	try:
		global JEEDOM_SOCKET_MESSAGE
		if not JEEDOM_SOCKET_MESSAGE.empty():
			logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
			message = json.loads(jeedom_utils.stripped(JEEDOM_SOCKET_MESSAGE.get()))
			if message['apikey'] != _apikey:
				logging.error("Invalid apikey from socket : " + str(message))
				return
			if test_edisio(message['data']):
				jeedom_serial.flushOutput()
				jeedom_serial.flushInput()
				logging.debug("------------------------------------------------")
				logging.debug("Incoming message from socket")
				logging.debug("Send\t\t\t= " + jeedom_utils.ByteToHex(message['data'].decode('hex')))
				logging.debug("Packet Length\t\t= " + jeedom_utils.ByteToHex(message['data'].decode('hex')[0]))
				logging.debug("Write message to serial port : " + jeedom_utils.ByteToHex(message['data'].decode('hex')))
				logging.debug("Write 1")
				jeedom_serial.write(message['data'].decode('hex'))
				time.sleep(0.14)
				logging.debug("Write 2")
				jeedom_serial.write(message['data'].decode('hex'))
				time.sleep(0.14)
				logging.debug("Write 3")
				jeedom_serial.write(message['data'].decode('hex'))
			else:
				logging.error("Invalid message from socket : " + str(message))
	except Exception,e:
		logging.error(str(e))

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

_log_level = "error"
_socket_port = 55005
_socket_host = 'localhost'
_device = 'auto'
_pidfile = '/tmp/edisiod.pid'
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

jeedom_utils.set_log_level(_log_level)

logging.info('Start edisiod')
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