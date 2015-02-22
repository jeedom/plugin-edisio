#!/usr/bin/python
# coding=UTF-8

# ------------------------------------------------------------------------------
#	
#	RFX_COMMAND.PY
#	
#	2013 Sebastian Sjoholm, sebastian.sjoholm@gmail.com
#
#	All credits for this code goes to the stackoverflow.com and posting;
#	http://stackoverflow.com/questions/16542422/asynchronous-subprocess-with-timeout
#
#	Author: epicbrew
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#	
#	Website
#	http://code.google.com/p/edisiocmd/
#
#	$Rev: 464 $
#	$Date: 2013-05-01 22:41:36 +0200 (Wed, 01 May 2013) $
#
# ------------------------------------------------------------------------------

# --------------------------------------------------------------------------

import logging
import subprocess
import threading

logger = logging.getLogger('edisiocmd')

class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None
	
	def run(self, timeout):
		def target():
			logger.debug("Thread started, timeout = " + str(timeout)+", command : "+str(self.cmd))
			self.process = subprocess.Popen(self.cmd, shell=True)
			self.process.communicate()
			self.timer.cancel()
		
		def timer_callback():
			logger.debug("Thread timeout, terminate it")
			if self.process.poll() is None:
				try:
					self.process.kill()
				except OSError as error:
					logger.error("Error: %s " % error)
				logger.debug("Thread terminated")
			else:
				logger.debug("Thread not alive")
			
		thread = threading.Thread(target=target)
		self.timer = threading.Timer(int(timeout), timer_callback)
		self.timer.start()
		thread.start()

# ----------------------------------------------------------------------------
