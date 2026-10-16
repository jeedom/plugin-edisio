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
import sys
import os
import time
import datetime
import argparse
import binascii
from threading import Thread, Event
import signal
import traceback
import json

from jeedom.jeedom import jeedom_com, jeedom_socket, jeedom_serial, jeedom_utils, JEEDOM_SOCKET_MESSAGE
import globals

_decode_value = {'01': 1, '02': 0, '03': 'toggle', '04': 'toggle', '05': 'toggle', '06': 'toggle', '07': 'up', '08': 'toggle', '09': 1, '0A': 0, '0B': 0, '0C': 0, '0D': 0, '0E': 0, '0F': 0, '10': 0, '11': 0,
                 '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '1A': 1, '1F': 0, '20': 0, '21': 0, 'F1': 20, 'F2': 20, 'F3': 30, 'F4': 40, 'F5': 50, 'F6': 60, 'F7': 70, 'F8': 80, 'F9': 90, 'FA': 100}


# MID reported as a button/value ('bt' + 'value')
_SIMPLE_VALUE_MID = {'01', '02', '03', '04', '05', '07', '09', '17', '18', '0C', '0F'}
# MID without decoding: frames are dropped
_IGNORED_MID = {'06', '10', '11', '12', '13', '14', '15', '16', '0B', '0D', '0E', '1B', '1E', '1F', '20', '21', '22', '23'}
# MID 1D (door/window sensor): CMD -> state
_STATE_BY_CMD = {'0B': '1', '0A': '2', '09': '3'}


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
            logging.debug("Time: %s - timer waiting for timeout in %.2f..." %
                          (time.asctime(), self.interval))
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        logging.debug("Time: %s - timer finished!" % time.asctime())

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            logging.debug("Time: %s - timer resetting to %.2f..." %
                          (time.asctime(), interval))
            self.interval = interval
        else:
            logging.debug("Time: %s - timer resetting..." % time.asctime())

        self.resetted = True
        self.finished.set()
        self.finished.clear()


DimOff_threads = {}


def sendDimOff(key, action):
    globals.JEEDOM_COM.add_changes('devices::'+key, action)
    del DimOff_threads[key]


def decodePacket(message):
    global _prevMessage
    global _prevDatetime
    global _timerDatetime
    unixtime_utc_check = datetime.datetime.utcnow()
    logging.debug("decodePacket : Incoming message (%s)", jeedom_utils.ByteToHex(message))
    if not test_edisio(jeedom_utils.ByteToHex(message)):
        logging.error("The incoming message is invalid (%s)", jeedom_utils.ByteToHex(message))
        return
    raw_message = jeedom_utils.ByteToHex(message).replace(' ', '')
    PID = (jeedom_utils.ByteToHex(message[3]) + jeedom_utils.ByteToHex(message[4]) +
           jeedom_utils.ByteToHex(message[5]) + jeedom_utils.ByteToHex(message[6]))
    BID = jeedom_utils.ByteToHex(message[7])
    MID = jeedom_utils.ByteToHex(message[8])
    BL = jeedom_utils.ByteToHex(message[9])
    RMAX = jeedom_utils.ByteToHex(message[10])
    CMD = jeedom_utils.ByteToHex(message[12])
    if len(message) > 16:
        DATA = ''.join(jeedom_utils.ByteToHex(b) for b in message[13:-3])
    else:
        DATA = 'None'
    clean_message = PID + BID + MID + RMAX + CMD + DATA

    if CMD == '07' and MID == '01':
        dimmingOff_thread = DimOff_threads.get(PID + BID)
        if dimmingOff_thread is not None:
            if clean_message == _prevMessage and unixtime_utc_check < (_timerDatetime + datetime.timedelta(milliseconds=800)):
                logging.debug("Too soon to refresh timer")
            else:
                logging.debug("Thread exists resetting")
                _timerDatetime = unixtime_utc_check
                dimmingOff_thread.reset(1)
        else:
            logging.debug("Thread not exists creating")
            BLDIM = int((int(BL, 16) / 3.3) * 10)
            dimOff = {'id': PID, 'battery': str(BLDIM), 'mid': MID, 'bt': BID, 'value': 'down'}
            dimmingOff = TimerReset(1, function=sendDimOff, args=(PID + BID, dimOff))
            DimOff_threads[PID + BID] = dimmingOff
            _timerDatetime = unixtime_utc_check
            dimmingOff.start()
        if clean_message == _prevMessage and unixtime_utc_check < (_prevDatetime + datetime.timedelta(milliseconds=4000)):
            return
    elif clean_message == _prevMessage and unixtime_utc_check < (_prevDatetime + datetime.timedelta(milliseconds=200)):
        logging.debug("Message already decode, ignore")
        return

    _prevMessage = clean_message
    _prevDatetime = unixtime_utc_check
    BL = int((int(BL, 16) / 3.3) * 10)
    action = {'id': PID, 'battery': str(BL), 'mid': MID, 'raw': raw_message}
    key = PID + MID + CMD + BID
    value = _decode_value.get(CMD, '')

    if MID in _IGNORED_MID:
        return
    if MID in _SIMPLE_VALUE_MID:
        action['bt'] = BID
        action['value'] = str(value)
    elif MID == '08':
        try:
            temperature = float(int(DATA[3:4] + DATA[0:2], 16)) / 100
        except Exception as e:
            logging.error("Error on temperature decode %s", e)
            return
        action['temperature'] = str(temperature)
    elif MID == '1D':
        state = _STATE_BY_CMD.get(CMD)
        if state:
            action['state'] = state

    logging.debug('Decode data : %s', action)
    try:
        if len(action) <= 4:
            return
        if action['id'] not in globals.KNOWN_DEVICES and not globals.INCLUDE_MODE:
            return
        globals.JEEDOM_COM.add_changes('devices::' + key, action)
    except Exception:
        pass

    return

# ----------------------------------------------------------------------------


def test_edisio(message):
    try:
        message = message.replace(' ', '')
    except Exception:
        logging.debug("Error: Removing white spaces")
        return False
    logging.debug(message)
    try:
        int(message, 16)
    except Exception:
        logging.debug("Error: Packet not hex format")
        return False
    if len(message) % 2:
        logging.debug("Error: Packet length not even")
        return False
    raw = binascii.unhexlify(message)
    if len(raw) < 16:
        logging.debug("Error: Packet length is not valid (<16)")
        return False
    for index, expected in ((0, "6C"), (1, "76"), (2, "63"), (-1, "0A"), (-2, "0D"), (-3, "64")):
        actual = jeedom_utils.dec2hex(raw[index])
        if actual != expected:
            logging.debug("Error: Packet byte %d is not %s : %s", index, expected, actual)
            return False
    return True

# ----------------------------------------------------------------------------


def read_edisio():
    message = None
    try:
        byte = jeedom_serial.read()
    except Exception as e:
        logging.error("Error in read_edisio: " + str(e))
        if str(e) == '[Errno 5] Input/output error':
            logging.error("Exit 1 because this exeption is fatal")
            shutdown()

    try:
        if str(jeedom_utils.ByteToHex(byte)) == '6C':
            logging.debug("read_edisio : 15 bytes after " +
                          str(jeedom_utils.ByteToHex(byte)))
            others_bytes = jeedom_serial.readbytes(15)
            logging.debug("read_edisio : others bytes are " +
                          str(jeedom_utils.ByteToHex(others_bytes)))
            message = b'' + byte + others_bytes
            logging.debug("Message: " + str(jeedom_utils.ByteToHex(message)))
            logging.debug("Test last bytes : " +
                          str(jeedom_utils.ByteToHex([message[-3], message[-2], message[-1]])))
            if str(jeedom_utils.ByteToHex([message[-3], message[-2], message[-1]])) != '64 0D 0A':
                message += jeedom_serial.readbytes(1)
            if str(jeedom_utils.ByteToHex([message[-3], message[-2], message[-1]])) != '64 0D 0A':
                message += jeedom_serial.readbytes(1)
            if str(jeedom_utils.ByteToHex([message[-3], message[-2], message[-1]])) != '64 0D 0A':
                message += jeedom_serial.readbytes(1)
            if str(jeedom_utils.ByteToHex([message[-3], message[-2], message[-1]])) != '64 0D 0A':
                message += jeedom_serial.readbytes(1)
            logging.debug("Message: " + str(jeedom_utils.ByteToHex(message)))
            decodePacket(message)
    except OSError as e:
        logging.error("Error in read_edisio on decode message : " +
                      str(jeedom_utils.ByteToHex(message))+" => "+str(e))

# ----------------------------------------------------------------------------


def listen():
    logging.debug("Start listening...")
    logging.debug("Serial openning...")
    jeedom_serial.open()
    logging.debug("Socket opening...")
    jeedom_socket.open()
    logging.debug("Serial flushOutput...")
    jeedom_serial.flushOutput()
    logging.debug("Serial flushInput...")
    jeedom_serial.flushInput()
    logging.debug("Loop listening...")
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
        if not JEEDOM_SOCKET_MESSAGE.empty():
            logging.debug("Message received in socket JEEDOM_SOCKET_MESSAGE")
            message = json.loads(JEEDOM_SOCKET_MESSAGE.get())
            logging.debug("Message received in socket %s", message)
            if message['apikey'] != _apikey:
                logging.error("Invalid apikey from socket : %s", message)
                return
            if message['cmd'] == 'add':
                logging.debug('Add device : %s', message['device'])
                if 'id' in message['device']:
                    globals.KNOWN_DEVICES[message['device']
                                          ['id']] = message['device']['id']
            elif message['cmd'] == 'remove':
                logging.debug('Remove device : %s', message['device'])
                if 'id' in message['device'] and message['device']['id'] in globals.KNOWN_DEVICES:
                    del globals.KNOWN_DEVICES[message['device']['id']]
            elif message['cmd'] == 'include_mode':
                if message['state'] == "1":
                    logging.debug('Enter in include mode')
                    globals.INCLUDE_MODE = True
                else:
                    logging.debug('Leave in include mode')
                    globals.INCLUDE_MODE = False
                globals.JEEDOM_COM.send_change_immediate(
                    {'include_mode': message['state']})
            elif message['cmd'] == 'send':
                if isinstance(message['data'], list):
                    for data in message['data']:
                        logging.debug(data)
                        send_edisio(data)
                else:
                    try:
                        logging.debug(message['data'])
                        send_edisio(message['data'])
                    except Exception as e:
                        logging.error('Send message command to edisio error : %s', e)
    except Exception as e:
        logging.error('Error on read socket : %s', e)

# ----------------------------------------------------------------------------


def send_edisio(message):
    logging.debug("send_edisio : Incoming message (" + message + ")")
    if test_edisio(message):
        jeedom_serial.flushOutput()
        jeedom_serial.flushInput()
        logging.debug("------------------------------------------------")
        logging.debug("Incoming message from socket")
        logging.debug("Message\t\t\t= " + message)
        logging.debug("Send\t\t\t= " +
                      jeedom_utils.ByteToHex(binascii.unhexlify(message)))
        logging.debug("Packet Length\t\t= " +
                      jeedom_utils.dec2hex(binascii.unhexlify(message)[0]))
        logging.debug("Write message to serial port : " +
                      jeedom_utils.ByteToHex(binascii.unhexlify(message)))
        logging.debug("Write 1")
        jeedom_serial.write(binascii.unhexlify(message))
        time.sleep(0.14)
        logging.debug("Write 2")
        jeedom_serial.write(binascii.unhexlify(message))
        time.sleep(0.14)
        logging.debug("Write 3")
        jeedom_serial.write(binascii.unhexlify(message))
        time.sleep(0.02)
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
    except Exception:
        pass
    try:
        jeedom_socket.close()
    except Exception:
        pass
    try:
        jeedom_serial.close()
    except Exception:
        pass
    logging.debug("Exit 0")
    sys.stdout.flush()
    os._exit(0)

# ----------------------------------------------------------------------------


_log_level = "error"
_socket_port = 55005
_socket_host = '127.0.0.1'
_device = 'auto'
_pidfile = '/tmp/edisiod.pid'
_apikey = ''
_callback = ''
_serial_rate = 9600
_serial_timeout = 9
_cycle = 0.3
_prevMessage = ''
_prevDatetime = datetime.datetime.utcnow()
_timerDatetime = datetime.datetime.utcnow()

parser = argparse.ArgumentParser(description='Edisio Daemon for Jeedom plugin')
parser.add_argument("--device", help="Device", type=str)
parser.add_argument("--socketport", help="Socketport for server", type=int)
parser.add_argument("--loglevel", help="Log Level for the daemon", type=str)
parser.add_argument("--callback", help="Callback", type=str)
parser.add_argument("--apikey", help="Apikey", type=str)
parser.add_argument("--cycle", help="Cycle to send event", type=float)
parser.add_argument("--pid", help="Pid file", type=str)
args = parser.parse_args()

if args.device:
    _device = args.device
if args.socketport:
    _socket_port = args.socketport
if args.loglevel:
    _log_level = args.loglevel
if args.callback:
    _callback = args.callback
if args.apikey:
    _apikey = args.apikey
if args.pid:
    _pidfile = args.pid
if args.cycle:
    _cycle = args.cycle

jeedom_utils.set_log_level(_log_level)

logging.info('Start edisiod')
logging.info('Log level : %s', _log_level)
logging.debug('Socket port : %s', _socket_port)
logging.debug('Socket host : %s', _socket_host)
logging.debug('PID file : %s', _pidfile)
logging.info('Device : %s', _device)
logging.debug('Callback : %s', _callback)
logging.debug('Cycle : %s', _cycle)
logging.debug('Serial rate : %s', _serial_rate)
logging.debug('Serial timeout : %s', _serial_timeout)

if _device == 'auto':
    _device = jeedom_utils.find_tty_usb('067b', '2303')
    logging.info('Find device : %s', _device)

if _device is None:
    _device = jeedom_utils.find_tty_usb('0403', '6001', 'edisio')
    logging.info('Find device : %s', _device)

if _device is None:
    logging.error('No device found')
    shutdown()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

try:
    jeedom_utils.write_pid(_pidfile)
    globals.JEEDOM_COM = jeedom_com(apikey=_apikey, url=_callback, cycle=_cycle)
    if not globals.JEEDOM_COM.test():
        logging.error('Network communication issues. Please fixe your Jeedom network configuration.')
        shutdown()
    jeedom_serial = jeedom_serial(device=_device, rate=_serial_rate, timeout=_serial_timeout)
    jeedom_socket = jeedom_socket(port=_socket_port, address=_socket_host)
    listen()
except Exception as e:
    logging.error('Fatal error : %s ', e)
    logging.debug(traceback.format_exc())
    shutdown()
