import sys
import os
import time
import logging
from os.path import join

try:
	from jeedom.jeedom import *
except ImportError:
	print "Error: importing module from jeedom folder"
	sys.exit(1)

print 'import -> ok'

jeedom = jeedom_com(url = 'http://127.0.0.1/plugins/edisio/core/php/jeeEdisio.php',apikey = '451321321321',log_level=logging.DEBUG)
jeedom.add_changes("toto::plop::tata","test")
jeedom.add_changes("toto::plop::tata2","test2")