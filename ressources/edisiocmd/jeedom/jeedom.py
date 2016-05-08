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
#

import time
import logging
import threading
import requests
import datetime
import collections

# ------------------------------------------------------------------------------

class jeedom_com():
	def __init__(self,apikey = '',url = '',cycle = 0.5,changes = {},logger = None,log_level=logging.ERROR):
		self.apikey = apikey
		self.url = url
		self.cycle = cycle
		self.changes = changes
		self.logger = logger
		if( logger is None):
			self.logger = logging
			self.logger.basicConfig(level=log_level,format='%(levelname)s:%(message)s')
		else:
			self.logger = logger
		self.send_changes_async()

	def send_changes_async(self):
		try:
			if len(self.changes) == 0:
				resend_changes = threading.Timer(self.cycle, self.send_changes_async)
				resend_changes.start() 
				return
			start_time = datetime.datetime.now()
			changes = self.changes
			self.changes = {}
			try:
				self.logger.debug('Send to jeedom :  %s' % (str(changes),))
				r = requests.post(self.url + '?apikey=' + self.apikey, json=changes, timeout=(0.5, 120), verify=False)
				if r.status_code != requests.codes.ok:
					self.logger.error('Error on send request to jeedom, return code %s' % (str(r.status_code),))
			except Exception as error:
				self.logger.error('Error on send request to jeedom %s' % (str(error),))
			dt = datetime.datetime.now() - start_time
			ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
			timer_duration = self.cycle - ms
			if timer_duration < 0.1:
				timer_duration = 0.1
			resend_changes = threading.Timer(timer_duration, self.send_changes_async)
			resend_changes.start() 
		except Exception as error:
			self.logger.error('Critical error on  send_changes_async %s' % (str(error),))
			resend_changes = threading.Timer(self.cycle, self.send_changes_async)
			resend_changes.start() 
		
	def add_changes(self,key,value):
		if key.find('::') != -1:
			tmp_changes = {}
			changes = value
			for k in reversed(key.split('::')):
				if k not in tmp_changes:
					tmp_changes[k] = {}
				tmp_changes[k] = changes
				changes = tmp_changes
				tmp_changes = {}
			self.merge_dict(self.changes,changes)
		else:
			self.changes[key] = value

	def send_change_immediate(self,change):
		try:
			self.logger.debug('Send to jeedom :  %s' % (str(change),))
			r = requests.post(self.url + '?apikey=' + self.apikey, json=change, timeout=(0.5, 120), verify=False)
			if r.status_code != requests.codes.ok:
				self.logger.error('Error on send request to jeedom, return code %s' % (str(r.status_code),))
		except Exception as error:
			self.logger.error('Error on send request to jeedom %s' % (str(error),))

	def set_change(self,changes):
		self.changes = changes

	def get_change(self,changes):
		return self.changes

	def merge_dict(self,d1, d2):
	    """
	    Modifies d1 in-place to contain values from d2.  If any value
	    in d1 is a dictionary (or dict-like), *and* the corresponding
	    value in d2 is also a dictionary, then merge them in-place.
	    """
	    for k,v2 in d2.items():
	        v1 = d1.get(k) # returns None if v1 has no value for this key
	        if ( isinstance(v1, collections.Mapping) and 
	             isinstance(v2, collections.Mapping) ):
	            self.merge_dict(v1, v2)
	        else:
	            d1[k] = v2

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------