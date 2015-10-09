#/* This file is part of Jeedom.
# *
# * Jeedom is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * Jeedom is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
# */

__author__ = "Gevrey Loic"
__copyright__ = "Copyright 2012-2014, Gevrey Loic"
__license__ = "GPL"
__version__ = "0.3"
__maintainer__ = "Gevrey Loic"
__email__ = "loic@jeedom.com"
__status__ = "Development-Beta-1"
__date__ = "$Date: 2015-02-14 18:37:06 +0200$"

# Default modules
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
import re
import signal
import xml.dom.minidom as minidom
from optparse import OptionParser
import socket
import select
import inspect
from os.path import join

# EDISIOCMD modules
try:
	from lib.edisio_socket import *
except ImportError:
	print "Error: importing module from lib folder"
	sys.exit(1)

try:
	from lib.edisio_utils import *
except ImportError:
	print "Error: module lib/edisio_utils not found"
	sys.exit(1)

# Serial
try:
	import serial
except ImportError:
	pass

# ------------------------------------------------------------------------------
# VARIABLE CLASSS
# ------------------------------------------------------------------------------

class config_data:
	def __init__(
		self,
		serial_device = "auto",
		serial_rate = 9600,
		serial_timeout = 9,
		trigger = "",
		trigger_timeout = 10,
		loglevel = "info",
		logfile = "edisiocmd.log",
		program_path = "",
		sockethost = "",
		socketport = "",
		daemon_pidfile = "edisiocmd.pid",
		log_msg = False,
		log_msgfile = "",
		process_repeat_message = True,
		repeat_message_time = 999999999
		):

		self.serial_device = serial_device
		self.serial_rate = serial_rate
		self.serial_timeout = serial_timeout
		self.trigger_timeout = trigger_timeout
		self.loglevel = loglevel
		self.logfile = logfile
		self.program_path = program_path
		self.sockethost = sockethost
		self.socketport = socketport
		self.daemon_pidfile = daemon_pidfile
		self.log_msg = log_msg
		self.log_msgfile = log_msgfile
		self.trigger = trigger
		self.trigger_timeout = trigger_timeout
		self.process_repeat_message = process_repeat_message
		self.repeat_message_time = repeat_message_time

class cmdarg_data:
	def __init__(
		self,
		configfile = "",
		action = "",
		rawcmd = "",
		device = "",
		createpid = False,
		pidfile = "",
		printout_complete = True,
		):

		self.configfile = configfile
		self.action = action
		self.rawcmd = rawcmd
		self.device = device
		self.createpid = createpid
		self.pidfile = pidfile
		self.printout_complete = printout_complete

class edisiocmd_data:
	def __init__(
		self,
		reset = "0d00000000000000000000000000",
		status = "0d00000002000000000000000000",
		save = "0d00000006000000000000000000"
		):

		self.reset = reset
		self.status = status
		self.save = save

class serial_data:
	def __init__(
		self,
		port = None,
		rate = 9600,
		timeout = 9
		):

		self.port = port
		self.rate = rate
		self.timeout = timeout

# Store the trigger data from xml file
class trigger_data:
	def __init__(
		self,
		data = ""
		):

		self.data = data

# ----------------------------------------------------------------------------
# DEAMONIZE
# Credit: George Henze
# ----------------------------------------------------------------------------

def shutdown():
	# clean up PID file after us
	logger.debug("Shutdown")

	if cmdarg.createpid:
		logger.debug("Removing PID file " + str(cmdarg.pidfile))
		os.remove(cmdarg.pidfile)

	if serial_param.port is not None:
		logger.debug("Close serial port")
		serial_param.port.close()
		serial_param.port = None

	logger.debug("Exit 0")
	sys.stdout.flush()
	os._exit(0)
	
def handler(signum=None, frame=None):
	if type(signum) != type(None):
		logger.debug("Signal %i caught, exiting..." % int(signum))
		shutdown()

def daemonize():

	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

	os.setsid() 

	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	try:
		pid = os.fork() 
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

	dev_null = file('/dev/null', 'r')
	os.dup2(dev_null.fileno(), sys.stdin.fileno())

	if cmdarg.createpid == True:
		pid = str(os.getpid())
		logger.debug("Writing PID " + pid + " to " + str(cmdarg.pidfile))
		file(cmdarg.pidfile, 'w').write("%s\n" % pid)

# ----------------------------------------------------------------------------
# C __LINE__ equivalent in Python by Elf Sternberg
# http://www.elfsternberg.com/2008/09/23/c-__line__-equivalent-in-python/
# ----------------------------------------------------------------------------

def _line():
	info = inspect.getframeinfo(inspect.currentframe().f_back)[0:3]
	return '[%s:%d]' % (info[2], info[1])

# ----------------------------------------------------------------------------

##############################COMMAND###########################################

class Command(object):
	def __init__(self, url,data):
		self.url = url
		self.data = data
		self.process = None
	
	def run(self, timeout):
		def target():
			logger.debug("Send data to jeedom : "+self.url+' => '+str(self.data))
			requests.get(self.url, params=self.data,timeout= (0.5,float(timeout)),verify=False)
			
		thread = threading.Thread(target=target)
		thread.start()

def readbytes(number):
	"""
	Read x amount of bytes from serial port. 
	Credit: Boris Smus http://smus.com
	"""
	buf = ''
	for i in range(number):
		try:
			byte = serial_param.port.read()
		except IOError, e:
			print "Error: %s" % e
		except OSError, e:
			print "Error: %s" % e
		buf += byte

	return buf

def decodePacket(message):
	"""
	Decode incoming EDISIO message.
	"""
	global prevMessage;
	global prevDatetime;
	global current_sensor_data;
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
	unixtime_utc = int(time.time())

	# Verify incoming message
	if not test_edisio( ByteToHex(message) ):
		logger.error("The incoming message is invalid (" + ByteToHex(message) + ") Line: " + _line())
		if cmdarg.printout_complete == True:
			print "Error: The incoming message is invalid " + _line()
		return
	
	raw_message = ByteToHex(message)
	raw_message = raw_message.replace(' ', '')

	PID = ByteToHex(message[3]) + ByteToHex(message[4]) + ByteToHex(message[5]) + ByteToHex(message[6])
	BID = ByteToHex(message[7])
	MID = ByteToHex(message[8])
	BL = ByteToHex(message[9])
	RMAX = ByteToHex(message[10])
	RC = ByteToHex(message[11])
	CMD = ByteToHex(message[12])
	DATA = 'None'

	if len(message) > 16:
		DATA = ''
		for i in range(0,len(message) - 16):
			DATA += ByteToHex(message[13 + i])

	clean_message = str(PID) + str(BID) + str(MID) + str(RMAX) + str(CMD) + str(DATA)

	if clean_message == prevMessage and unixtime_utc < (prevDatetime+1) :
		logger.debug("Message already decode, ignore")
		return

	prevMessage = clean_message
	prevDatetime = unixtime_utc

	decode_string = "\nPID\t\t\t= " + str(PID);
	decode_string += "\nBID\t\t\t= " + str(BID);
	decode_string += "\nMID\t\t\t= " + str(MID);
	decode_string += "\nBL\t\t\t= " + str(BL);
	decode_string += "\nRMAX\t\t\t= " + str(RMAX);
	decode_string += "\nRC\t\t\t= " + str(RC);
	decode_string += "\nCMD\t\t\t= " + str(CMD);
	decode_string += "\nDATA\t\t\t= " + str(DATA);

	BL = int((int(BL, 16) / 3.3) * 10)

	action = {'id' : str(PID), 'battery' : str(BL), 'mid' : str(MID),'apikey' : str(config.apikey)}

	key = str(PID)+str(MID)+str(CMD)
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
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '02':
		decode_string += "\nDecode model : \t\t= Emitter Channel 2"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '03':
		decode_string += "\nDecode model : \t\t= Emitter Channel 3"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '04':
		decode_string += "\nDecode model : \t\t= Emitter Channel 4"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '05':
		decode_string += "\nDecode model : \t\t= Emitter Channel 5"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '06':
		decode_string += "\nDecode model : \t\t= Energy Meter"

	if MID == '07':
		decode_string += "\nDecode model : \t\t= Motion Sensor (On/Off/Pulse)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '08':
		decode_string += "\nDecode model : \t\t= Temperature Sensor"
		try:
			temperature = float(int(DATA[3:4]+DATA[0:2],16)) / 100
		except Exception, e:
			logger.debug("Error on temperature decode "+str(e))
			return

		if key in current_sensor_data and 'updateTime' in current_sensor_data[key] : 
			action['time_between_message'] = str(unixtime_utc - current_sensor_data[key]['updateTime'])
			decode_string += "\nTime between message\t= " + str(unixtime_utc - current_sensor_data[key]['updateTime'])

		if not config.process_repeat_message and key in current_sensor_data and config.repeat_message_time > (unixtime_utc - current_sensor_data[key]['updateTime']):
			if current_sensor_data[key]['temperature'] <> temperature:
				action['temperature'] = str(temperature)
		else :
			action['temperature'] = str(temperature)

	
		current_sensor_data[key] = {'temperature' : temperature, 'updateTime' : unixtime_utc}

		if 'temperature' in action :
			command = Command(config.trigger_url,action)
			command.run(timeout=config.trigger_timeout)


	if MID == '09':
		decode_string += "\nDecode model : \t\t= Door Sensor (On/Off/Pulse)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

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
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '18':
		decode_string += "\nDecode model : \t\t= Emitter 2 Channels (Button)"
		action['bt'] = str(BID)
		action['value'] = str(value)
		command = Command(config.trigger_url,action)
		command.run(timeout=config.trigger_timeout)

	if MID == '0B':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (On/Off)"

	if MID == '0E':
		decode_string += "\nDecode model : \t\t= Thermostat"

	if MID == '0F':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (Heater On/Off)"

	if MID == '0C':
		decode_string += "\nDecode model : \t\t= Receiver 1 Output (Pilot Wire Functions)"

	if MID == '0D':
		decode_string += "\nDecode model : \t\t= Receiver 2 Outputs (1x Open/Close)"

	if MID == '1B':
		decode_string += "\nDecode model : \t\t= IR transmitter (Trigger)"

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


	logger.debug("Decode packet : "+decode_string)
	if config.log_msg == True:
		try:
			data = str(ByteToHex(message))
			data = data.replace(' ', '')
			file = open(config.log_msgfile,"a+")
			file.write("---------------------------------\n")
			file.write(time.strftime("%Y-%m-%d %H:%M:%S")+' Message : '+data+decode_string + "\n")
			file.close()
		except Exception, e:
			logger.error("Error when trying to write message log")
			logger.error("Exception: %s" % str(e))
			pass

	# decodePackage END
	return

# ----------------------------------------------------------------------------
	
def read_socket():

	global messageQueue
	
	if not messageQueue.empty():
		logger.debug("Message received in socket messageQueue")
		message = stripped(messageQueue.get())
		if test_edisio( message ):
			
			# Flush buffer
			serial_param.port.flushOutput()
			logger.debug("SerialPort flush output")
			serial_param.port.flushInput()
			logger.debug("SerialPort flush input")
			
			timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
					
			if cmdarg.printout_complete == True:
				print "------------------------------------------------"
				print "Incoming message from socket"
				print "Send\t\t\t= " + ByteToHex( message.decode('hex') )
				print "Date/Time\t\t= " + timestamp
				print "Packet Length\t\t= " + ByteToHex( message.decode('hex')[0] )

			logger.debug("Write message to serial port : " + ByteToHex( message.decode('hex')))
			serial_param.port.write( message.decode('hex') )
			logger.debug("Write 1")
			time.sleep(0.14)
			serial_param.port.write( message.decode('hex') )
			logger.debug("Write 2")
			time.sleep(0.14)
			serial_param.port.write( message.decode('hex') )
			logger.debug("Write 3")
			
		else:
			logger.error("Invalid message from socket. Line: " + _line())
			if cmdarg.printout_complete == True:
				print "------------------------------------------------"
				print "Invalid message from socket"

# ----------------------------------------------------------------------------

def test_edisio( message ):
	"""
	Test, filter and verify that the incoming message is valid
	Return true if valid, False if not
	"""
		
	# Remove all invalid characters
	message = stripped(message)
	
	# Remove any whitespaces
	try:
		message = message.replace(' ', '')
	except Exception:
		logger.debug("Error: Removing white spaces")
		return False
	
	# Test the string if it is hex format
	try:
		int(message,16)
	except Exception:
		logger.debug("Error: Packet not hex format")
		return False
	
	# Check that length is even
	if len(message) % 2:
		logger.debug("Error: Packet length not even")
		return False

	if len(message.decode('hex')) < 16:
		logger.debug("Error: Packet length is not valid (<16)")
		return False
	
	# Check that first byte is not 6C
	if ByteToHex(message.decode('hex')[0]) <> "6C":
		logger.debug("Error: Packet first byte is not 6C : "+str(ByteToHex(message.decode('hex')[0])))
		return False

	if ByteToHex(message.decode('hex')[1]) <> "76":
		logger.debug("Error: Packet second byte is not 76 : "+str(ByteToHex(message.decode('hex')[0])))
		return False

	if ByteToHex(message.decode('hex')[2]) <> "63":
		logger.debug("Error: Packet third byte is not 63 : "+str(ByteToHex(message.decode('hex')[0])))
		return False

	if ByteToHex(message.decode('hex')[-1]) <> "0A":
		logger.debug("Error: Packet last byte is not 0A : "+str(ByteToHex(message.decode('hex')[-1])))
		return False

	if ByteToHex(message.decode('hex')[-2]) <> "0D":
		logger.debug("Error: Packet -2 byte is not 0D : "+str(ByteToHex(message.decode('hex')[-2])))
		return False

	if ByteToHex(message.decode('hex')[-3]) <> "64":
		logger.debug("Error: Packet -3 byte is not 64 : "+str(ByteToHex(message.decode('hex')[-3])))
		return False
	
	# Length more than one byte
	if not len(message.decode('hex')) > 1:
		logger.debug("Error: Packet is not longer than one byte")
		return False

	return True
			
# ----------------------------------------------------------------------------

def send_edisio( message ):
	"""
	Decode and send raw message to RFX device
	"""
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	
	if cmdarg.printout_complete == True:
		print "------------------------------------------------"
		print "Send\t\t\t= " + ByteToHex( message )
		print "Date/Time\t\t= " + timestamp
		print "Packet Length\t\t= " + ByteToHex( message[0] )
		
		try:
			decodePacket( message )
		except KeyError:
			print("Error: unrecognizable packet")
	
	serial_param.port.write( message )
	time.sleep(1)

# ----------------------------------------------------------------------------

def read_edisio():
	"""
	Read message from EDISIO and decode the decode the message
	"""
	message = None
	byte = None
	
	try:
		
		try:
			if serial_param.port.inWaiting() != 0:
				byte = serial_param.port.read()
		except IOError, err:
			print("Error: " + str(err))
			logger.error("Serial read error: %s, Line: %s" % (str(err),_line()))
		
		if str(ByteToHex(byte)) == '6C' :
			message = byte + readbytes(15)
			if str(ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += readbytes(1)
			if str(ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += readbytes(1)
			if str(ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += readbytes(1)
			if str(ByteToHex(message[-3]+message[-2]+message[-1])) <> '64 0D 0A' :
				message += readbytes(1)
			logger.debug("Message: " + str(ByteToHex(message)))
			decodePacket(message);

	except OSError, e:
		logger.error("Error in message: " + str(ByteToHex(message)) + " Line: " + _line())
		logger.error("Traceback: " + traceback.format_exc())
		print("------------------------------------------------")
		print("Received\t\t= " + ByteToHex( message ))
		traceback.format_exc()

# ----------------------------------------------------------------------------

def read_config( configFile, configItem):
	"""
	Read item from the configuration file
	"""
	if os.path.exists( configFile ):

		#open the xml file for reading:
		f = open( configFile,'r')
		data = f.read()
		f.close()

		try:
			dom = minidom.parseString(data)
		except:
			print "Error: problem in the config.xml file, cannot process it"
			logger.debug('Error in config.xml file')
			
		# Get config item
	 	logger.debug('Get the configuration item: ' + configItem)
		
		try:
			xmlTag = dom.getElementsByTagName( configItem )[0].toxml()
			logger.debug('Found: ' + xmlTag)
			xmlData = xmlTag.replace('<' + configItem + '>','').replace('</' + configItem + '>','')
			logger.debug('--> ' + xmlData)
		except:
			logger.debug('The item tag not found in the config file')
			xmlData = ""
 	else:
 		logger.error("Error: Config file does not exists. Line: " + _line())
 		
	return xmlData

# ----------------------------------------------------------------------------

def print_version():
	"""
	Print EDISIOCMD version, build and date
	"""
	logger.debug("print_version")
 	print "EDISIOCMD Version: " + __version__
 	print __date__.replace('$', '')
 	logger.debug("Exit 0")
 	sys.exit(0)

# ----------------------------------------------------------------------------

def check_pythonversion():
	"""
	Check python version
	"""
	if sys.hexversion < 0x02060000:
		print "Error: Your Python need to be 2.6 or newer, please upgrade."
		sys.exit(1)

# ----------------------------------------------------------------------------

def option_simulate(indata):
	"""
	Simulate incoming packet, decode and process
	"""

	# Remove all spaces
	for x in string.whitespace:
		indata = indata.replace(x,"")
	
	# Cut into hex chunks
	try:
		message = indata.decode("hex")
	except:
		logger.error("Error: the input data is not valid. Line: " + _line())
		print "Error: the input data is not valid"
		sys.exit(1)
	
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

	# Printout
	if cmdarg.printout_complete:
		print "------------------------------------------------"
		print "Received\t\t= " + indata
		print "Date/Time\t\t= " + timestamp
	
	# Verify that the incoming value is hex
	try:
		hexval = int(indata, 16)
	except:
		logger.error("Error: the input data is invalid hex value. Line: " + _line())
		print "Error: the input data is invalid hex value"
		sys.exit(1)
				
	# Decode it
	try:
		decodePacket( message )
	except Exception as err:
		logger.error("Error: unrecognizable packet (" + ByteToHex(message) + ") Line: " + _line())
		logger.error("Error: %s" %err)
		print "Error: unrecognizable packet"
		
	logger.debug('Exit 0')
	sys.exit(0)

# ----------------------------------------------------------------------------

def option_listen():
	"""
	Listen to EDISIO device and process data, exit with CTRL+C
	"""
	logger.debug("Start listening...")
	
	logger.debug("Open serial port")
	open_serialport()

	try:
		serversocket = RFXcmdSocketAdapter(config.sockethost,int(config.socketport))
	except Exception as err:
		logger.error("Error starting socket server. Line: " + _line())
		logger.error("Error: %s" % str(err))
		print "Error: can not start server socket, another instance already running?"
		exit(1)
	if serversocket.netAdapterRegistered:
		logger.debug("Socket interface started")
	else:
		logger.debug("Cannot start socket interface")

	
	# Flush buffer
	logger.debug("Serialport flush output")
	serial_param.port.flushOutput()
	logger.debug("Serialport flush input")
	serial_param.port.flushInput()

	try:
		while 1:
			# Let it breath
			# Without this sleep it will cause 100% CPU in windows
			time.sleep(0.05)
			
			rawcmd = read_edisio()
			if rawcmd:
				logger.debug("Processed: " + str(rawcmd))

			read_socket()
			
	except KeyboardInterrupt:
		logger.debug("Received keyboard interrupt")
		logger.debug("Close server socket")
		serversocket.netAdapter.shutdown()
		
		logger.debug("Close serial port")
		close_serialport()
		
		print("\nExit...")
		pass

# ----------------------------------------------------------------------------

def option_send():
	"""
	Send command to RFX device
	
	"""
	
	logger.debug("Send message to RFX device")

	# Open serial port
	logger.debug("Open serial port")
	open_serialport()

	# Remove any whitespaces	
	cmdarg.rawcmd = cmdarg.rawcmd.replace(' ', '')
	logger.debug("Message: " + cmdarg.rawcmd)

	# Test the string if it is hex format
	try:
		int(cmdarg.rawcmd,16)
	except ValueError:
		print "Error: invalid rawcmd, not hex format"
		sys.exit(1)		
	
	# Check that first byte is not 00
	if ByteToHex(cmdarg.rawcmd.decode('hex')[0]) == "00":
		print "Error: invalid rawcmd, first byte is zero"
		sys.exit(1)
	
	# Check if string is the length that it reports to be
	cmd_len = int( ByteToHex(cmdarg.rawcmd.decode('hex')[0]),16 )
	if not len(cmdarg.rawcmd.decode('hex')) == (cmd_len + 1):
		print "Error: invalid rawcmd, invalid length"
		sys.exit(1)

	if cmdarg.rawcmd:
		timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
		if cmdarg.printout_complete == True:
			print "------------------------------------------------"
			print "Send\t\t\t= " + ByteToHex( cmdarg.rawcmd.decode('hex') )
			print "Date/Time\t\t= " + timestamp
			print "Packet Length\t\t= " + ByteToHex( cmdarg.rawcmd.decode('hex')[0] )
			try:
				decodePacket( cmdarg.rawcmd.decode('hex') )
			except KeyError:
				print "Error: unrecognizable packet"

		logger.debug("Send message")
		serial_param.port.write( cmdarg.rawcmd.decode('hex') )
		time.sleep(1)
		logger.debug("Read response")
		read_edisio()

	logger.debug("Close serial port")
	close_serialport()

# ----------------------------------------------------------------------------

def read_configfile():
	"""
	Read items from the configuration file
	"""
	if os.path.exists( cmdarg.configfile ):

		# ----------------------
		# Serial device
		config.serial_device = read_config( cmdarg.configfile, "serial_device")
		if config.serial_device == 'auto':
			config.serial_device = find_tty_usb('067b','2303')
		config.serial_rate = read_config( cmdarg.configfile, "serial_rate")
		config.serial_timeout = read_config( cmdarg.configfile, "serial_timeout")
		
		# ----------------------
		# TRIGGER
		config.trigger_url = read_config( cmdarg.configfile, "trigger_url")
		config.apikey = read_config( cmdarg.configfile, "apikey")
		config.trigger_timeout = read_config( cmdarg.configfile, "trigger_timeout")

		# ----------------------
		config.sockethost = read_config( cmdarg.configfile, "sockethost")
		config.socketport = read_config( cmdarg.configfile, "socketport")

		# -----------------------
		# DAEMON
		config.daemon_pidfile = read_config( cmdarg.configfile, "daemon_pidfile")
		
		# ------------------------
		# LOG MESSAGES
		if (read_config(cmdarg.configfile, "log_msg") == "yes"):
			config.log_msg = True
		else:
			config.log_msg = False
		config.log_msgfile = read_config(cmdarg.configfile, "log_msgfile")

		# ------------------------
		# Process repaet message
		if (read_config(cmdarg.configfile, "process_repeat_message") == "yes"):
			config.process_repeat_message = True
		else:
			config.process_repeat_message = False

		config.repeat_message_time = int(read_config(cmdarg.configfile, "repeat_message_time"))

	else:
		# config file not found, set default values
		print "Error: Configuration file not found (" + cmdarg.configfile + ")"
		logger.error("Error: Configuration file not found (" + cmdarg.configfile + ") Line: " + _line())

# ----------------------------------------------------------------------------

def open_serialport():
	"""
	Open serial port for communication to the EDISIO device.
	"""

	# Check that serial module is loaded
	try:
		logger.debug("Serial extension version: " + serial.VERSION)
	except:
		print "Error: You need to install Serial extension for Python"
		logger.debug("Error: Serial extension for Python could not be loaded")
		logger.debug("Exit 1")
		sys.exit(1)

	# Check for serial device
	if config.device:
		logger.debug("Device: " + config.device)
	else:
		logger.error("Device name missing. Line: " + _line())
		print "Serial device is missing"
		logger.debug("Exit 1")
		sys.exit(1)

	# Open serial port
	logger.debug("Open Serialport")
	try:  
		serial_param.port = serial.Serial(config.device, serial_param.rate, timeout=serial_param.timeout)
	except serial.SerialException, e:
		logger.error("Error: Failed to connect on device " + config.device + " Line: " + _line())
		print "Error: Failed to connect on device " + config.device
		print "Error: " + str(e)
		logger.debug("Exit 1")
		sys.exit(1)

	if not serial_param.port.isOpen():
		serial_param.port.open()

# ----------------------------------------------------------------------------

def close_serialport():
	"""
	Close serial port.
	"""

	logger.debug("Close serial port")
	try:
		serial_param.port.close()
		logger.debug("Serial port closed")
	except:
		logger.error("Failed to close the serial port (" + device + ") Line: " + _line())
		print "Error: Failed to close the port " + device
		logger.debug("Exit 1")
		sys.exit(1)

# ----------------------------------------------------------------------------

def find_tty_usb(idVendor, idProduct):
    """find_tty_usb('067b', '2302') -> '/dev/ttyUSB0'"""
    # Note: if searching for a lot of pairs, it would be much faster to search
    # for the enitre lot at once instead of going over all the usb devices
    # each time.
    for dnbase in os.listdir('/sys/bus/usb/devices'):
        dn = join('/sys/bus/usb/devices', dnbase)
        if not os.path.exists(join(dn, 'idVendor')):
            continue
        idv = open(join(dn, 'idVendor')).read().strip()
        if idv != idVendor:
            continue
        idp = open(join(dn, 'idProduct')).read().strip()
        if idp != idProduct:
            continue
        for subdir in os.listdir(dn):
            if subdir.startswith(dnbase+':'):
                for subsubdir in os.listdir(join(dn, subdir)):
                    if subsubdir.startswith('ttyUSB'):
                        return join('/dev', subsubdir)

# ----------------------------------------------------------------------------

def logger_init(configFile, name, debug):
	program_path = os.path.dirname(os.path.realpath(__file__))
	dom = None
	if os.path.exists( configFile ):
		#open the xml file for reading:
		f = open( configFile,'r')
		data = f.read()
		f.close()
		try:
			dom = minidom.parseString(data)
		except Exception, e:
			print "Error: problem in the config.xml file, cannot process it"
			print "Exception: %s" % str(e)
		if dom:
		
			# Get loglevel from config file
			try:
				xmlTag = dom.getElementsByTagName( 'loglevel' )[0].toxml()
				loglevel = xmlTag.replace('<loglevel>','').replace('</loglevel>','')
			except:
				loglevel = "INFO"

			# Get logfile from config file
			try:
				xmlTag = dom.getElementsByTagName( 'logfile' )[0].toxml()
				logfile = xmlTag.replace('<logfile>','').replace('</logfile>','')
			except:
				logfile = os.path.join(program_path, "edisiocmd.log")
			
			loglevel = loglevel.upper()
			
			#formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
			formatter = logging.Formatter(fmt='%(asctime)s - %(threadName)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
			
			if debug:
				loglevel = "DEBUG"
				handler = logging.StreamHandler()
			else:
				handler = logging.FileHandler(logfile)
							
			handler.setFormatter(formatter)
			
			logger = logging.getLogger(name)
			logger.setLevel(logging.getLevelName(loglevel))
			logger.addHandler(handler)
			
			return logger

# ----------------------------------------------------------------------------

def main():

	global logger

	# Get directory of the edisiocmd script
	config.program_path = os.path.dirname(os.path.realpath(__file__))

	parser = OptionParser()
	parser.add_option("-d", "--device", action="store", type="string", dest="device", help="The serial device of the EDISIO, example /dev/ttyUSB0")
	parser.add_option("-x", "--simulate", action="store", type="string", dest="simulate", help="Simulate one incoming data message")
	parser.add_option("-s", "--sendmsg", action="store", type="string", dest="sendmsg", help="Send one message to RFX device")
	parser.add_option("-o", "--config", action="store", type="string", dest="config", help="Specify the configuration file")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Output all messages to stdout")
	parser.add_option("-V", "--version", action="store_true", dest="version", help="Print edisiocmd version information")
	parser.add_option("-D", "--debug", action="store_true", dest="debug", default=False, help="Debug printout on stdout")
	(options, args) = parser.parse_args()

	# ----------------------------------------------------------
	# CONFIG FILE
	if options.config:
		cmdarg.configfile = options.config
	else:
		cmdarg.configfile = os.path.join(config.program_path, "config.xml")

	# ----------------------------------------------------------
	# LOGHANDLER
	if options.debug:
		logger = logger_init(cmdarg.configfile,'edisiocmd', True)
	else:
		logger = logger_init(cmdarg.configfile,'edisiocmd', False)
	
	logger.debug("Python version: %s.%s.%s" % sys.version_info[:3])
	logger.debug("EDISIOCMD Version: " + __version__)
	logger.debug(__date__.replace('$', ''))

	# ----------------------------------------------------------
	# PROCESS CONFIG.XML
	logger.debug("Configfile: " + cmdarg.configfile)
	logger.debug("Read configuration file")
	read_configfile()

	# ----------------------------------------------------------
	# VERBOSE OUTPUT
	if options.verbose:
		logger.debug("Verbose printout " + _line())
		cmdarg.printout_complete = True
		print "EDISIOCMD Version " + __version__
	else:
		cmdarg.printout_complete = False

	# ----------------------------------------------------------
	# SERIAL
	if options.device:
		config.device = options.device
	elif config.serial_device:
		config.device = config.serial_device
	else:
		config.device = None

	# ----------------------------------------------------------
	# DAEMON
	logger.debug("Daemon")
	logger.debug("Check PID file")
	
	if config.daemon_pidfile:
		cmdarg.pidfile = config.daemon_pidfile
		cmdarg.createpid = True
		logger.debug("PID file '" + cmdarg.pidfile + "'")
	
		if os.path.exists(cmdarg.pidfile):
			print("PID file '" + cmdarg.pidfile + "' already exists. Exiting.")
			logger.debug("PID file '" + cmdarg.pidfile + "' already exists.")
			logger.debug("Exit 1")
			sys.exit(1)
		else:
			logger.debug("PID file does not exists")

	else:
		print("You need to set the --pidfile parameter at the startup")
		logger.error("Command argument --pidfile missing. Line: " + _line())
		logger.debug("Exit 1")
		sys.exit(1)

	logger.debug("Check platform")
	if sys.platform == 'win32':
		print "Daemonize not supported under Windows. Exiting."
		logger.error("Daemonize not supported under Windows. Line: " + _line())
		logger.debug("Exit 1")
		sys.exit(1)
	else:
		logger.debug("Platform: " + sys.platform)
		
		try:
			logger.debug("Write PID file")
			file(cmdarg.pidfile, 'w').write("pid\n")
		except IOError, e:
			logger.error("Line: " + _line())
			logger.error("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
			raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))

		logger.debug("Deactivate screen printouts")
		cmdarg.printout_complete = False

		logger.debug("Start daemon")
		daemonize()

	# ----------------------------------------------------------
	# SIMULATE
	if options.simulate:
		option_simulate(options.simulate)

	# ----------------------------------------------------------
	option_listen()

	# ----------------------------------------------------------
	# SEND MESSAGE
	if options.sendmsg:
		cmdarg.rawcmd = options.sendmsg
		option_send()
	
	logger.debug("Exit 0")
	sys.exit(0)
	
# ------------------------------------------------------------------------------

if __name__ == '__main__':

	# Init shutdown handler
	signal.signal(signal.SIGINT, handler)
	signal.signal(signal.SIGTERM, handler)

	# Init objects
	config = config_data()
	cmdarg = cmdarg_data()
	edisiocmd = edisiocmd_data()
	serial_param = serial_data()
	current_sensor_data = {}
	prevMessage = '';
	prevDatetime = '';

	# Check python version
	check_pythonversion()
	
	main()

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------
