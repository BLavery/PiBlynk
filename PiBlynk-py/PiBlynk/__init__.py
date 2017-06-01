#    USAGE:
#    from PiBlynk import Blynk
#    blynk = Blynk(token)     and some options - see Class Blynk


# BL  PiBlynk   V 0.3.5  28/5/17

# Python based Blynk library for Raspberry Pi

'''
Attribution
-----------
This library was inspired by, and leveraged from, the work of the WIPY project.
   https://github.com/wipy/wipy/blob/master/lib/blynk/BlynkLib.py
and then from
   https://github.com/youngsoul/BlynkLib

This version was targeted for Raspberry Pi, 
but being GPIO agnostic by default, it should run on a PC quite fine.
It is gpiozero-friendly, and if optioned, it can use gpiozero to auto-configure gpio pins set at APP.

''' 

# Original WiPy version licence follows:

    # This file is part of the Micro Python project, http://micropython.org/
    #
    # The MIT License (MIT)
    #
    # Copyright (c) 2015 Daniel Campora
    # Copyright (c) 2015 Volodymyr Shymanskyy
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.

    
import logging
import socket
import struct
import time
import threading
import sys
import math
python_version = sys.version_info[0]

logging.basicConfig(level=logging.ERROR)
# logging levels:  https://docs.python.org/2/howto/logging.html
# DEBUG INFO WARNING ERROR  CRITICAL      usually set down to CRITICAL


const = lambda x: x

HDR_LEN = const(5)
HDR_FMT = "!BHH"

MAX_MSG_PER_SEC = const(20)

MSG_RSP = const(0)
MSG_LOGIN = const(2)
MSG_PING = const(6)
MSG_TWEET = const(12)
MSG_EMAIL = const(13)
MSG_NOTIFY = const(14)
MSG_BRIDGE = const(15)
MSG_HW_SYNC = const(16)
MSG_HW_INFO = const(17)
MSG_PROPERTY = const(19)
MSG_HW = const(20)

STA_SUCCESS = const(200)

HB_PERIOD = const(10)
NON_BLK_SOCK = const(0)
MIN_SOCK_TO = const(1)  # 1 second
MAX_SOCK_TO = const(5)  # 5 seconds
RECONNECT_DELAY = const(2)  # 1 second
TASK_PERIOD_RES = const(50)  # 50 ms
IDLE_TIME_MS = const(5)  # 5 ms

RE_TX_DELAY = const(2)
MAX_TX_RETRIES = const(3)

MAX_VIRTUAL_PINS = const(128)

DISCONNECTED = 0
CONNECTING = 1
AUTHENTICATING = 2
AUTHENTICATED = 3

EAGAIN = const(11)


def now_in_ms():
    millis = int(round(time.time() * 1000))
    return millis


class VrPin:
    def __init__(self, read=None, write=None, blynk_ref=None, initial_state=None):
        self.read = read
        self.write = write
        self.state = initial_state if initial_state is not None else {}
        self.blynk_ref = blynk_ref


class HwPin:
    def __init__(self, read=None, write=None, blynk_ref=None, initial_state=None):
        self.read = read
        self.write = write
        self.state = initial_state if initial_state is not None else {}
        self.blynk_ref = blynk_ref


class UserTask:
    def __init__(self, task_handler, period_in_seconds, blynk, initial_state=None, always=False):
        self.task_handler = task_handler
        self.period_in_seconds = period_in_seconds if period_in_seconds > 0 else 1
        self.task_state = initial_state if initial_state is not None else {}
        self.blynk = blynk
        self._always = True if always == True else False
        
    def run_task(self):

        if self.task_handler and (self.blynk.state == AUTHENTICATED or self._always):
            new_s = self.task_handler(self.task_state)
            if new_s != None:
                self.task_state = new_s
            
        # then on return, task self-re-schedules:
        the_timer = threading.Timer(self.period_in_seconds, self.run_task) # a 1-shot
        the_timer.daemon = True
        the_timer.start()
        
class UserTimer:
    def __init__(self, task_handler, time_in_seconds, blynk, initial_state=None):
        self.task_handler = task_handler
        self.time_in_seconds = time_in_seconds
        self.task_state = initial_state if initial_state is not None else {}
        self.blynk = blynk
        
    def run_task(self):
        if self.task_handler:
            self.task_handler(self.task_state)
            
    def arm(self):   
        the_timer = threading.Timer(self.time_in_seconds, self.run_task) # a 1-shot
        the_timer.daemon = True
        the_timer.start()

class LCD:
    def __init__(self, blynk, pin):
        self._blynk = blynk
        self._pin = pin

    def Print(self, x, y, msg):
        self._blynk.virtual_write(self._pin,  [ "p", str(x%16), str(y%2),  msg])

    def cls(self):
        self._blynk.virtual_write(self._pin, "clr")
        
class ACCEL:
    # accel widget at APP sends a RAPID data stream, not adjustable.
    # This RPI-end widget buffers incoming data until wanted 
    # user should request the info as needed. [  .x  .y   .z  .pitch()    .roll()   ]
    # Dont use this class if you DO want the high-speed data.
    
    def __init__(self,  pin):
        self.x = 0.0  # out "right wing"
        self.y = 0.0  # ahead
        self.z = 0.0  # up
         # in m/s/s  ENU coordinates
        self.timestamp = None

    def pitch(self): # in degrees - nose up
        return 57.3*math.atan2(self.y, self.z)
        
    def roll(self):  # left wing up
        return 57.3*math.atan2(-self.x, self.z)

    def _virtual_write_incoming(self, val, pin, st):
        self.x = float(val[0])
        self.y = float(val[1])
        self.z = float(val[2])
        self.timestamp = time.time()
        
    
class GPS:

    def __init__(self, pin):
        self.lat = 0.0
        self.lon = 0.0
        self._lat0 = 0.0
        self._lon0 = 0.0
        self.timestamp = None

    def set_ref(self, lat0=None, lon0=None):
        self._lat0 = lat0 if lat0 else self.lat
        self._lon0 = lon0 if lon0 else self.lon
    
    def distance(self):  # from original position
        return self._getDistanceFromLatLonInKm(self._lat0,self._lon0,self.lat,self.lon)
        
    def direction(self):  # movement from original position
        d2r = math.pi/180
        dLon = d2r*(self.lon-self._lon0) 
        direc  = math.atan2(math.sin(dLon)*math.cos(d2r*self.lat), math.cos(d2r*self._lat0)*math.sin(d2r*self.lat)-math.sin(d2r*self._lat0)*math.cos(d2r*self.lat)*math.cos(dLon))
        return  ((direc * 180/math.pi) + 360) % 360
        # http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    def _virtual_write_incoming(self, val, pin, st):
        self.lat = float(val[0])
        self.lon = float(val[1])
        if self._lat0 == 0 and self._lon0 == 0:
            self.set_ref()
        self.timestamp = time.time()
            
    def _getDistanceFromLatLonInKm(self, lat1,lon1,lat2,lon2):
      R = 6371 # Radius of the earth in km
      d2r =  (math.pi/180)  # deg2rad 
      dLat = (lat2-lat1) * d2r
      dLon = (lon2-lon1) * d2r 
      a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos((lat1) * d2r) * math.cos((lat2)* d2r) * math.sin(dLon/2) * math.sin(dLon/2)
      c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
      return R * c; # Distance in km
      # http://stackoverflow.com/questions/18883601/function-to-calculate-distance-between-two-coordinates-shows-wrong
        
class SENSOR:
    # generic 1-value sensor that writes app->rpi eg light, prox, switch-button
    # "Buffers" the reading until actually wanted by application
    # user should make a request : "v = mySensor.value" when needed.
    
    def __init__(self, pin):
        self.value = ""
        self.timestamp = None


    def _virtual_write_incoming(self, val, pin, st):
        self.value = val[0]   # single value
        self.timestamp = time.time()
        
class BRIDGE: 
    def __init__(self, blynk, pin):
        self._blynk = blynk
        self._pin = pin
        
    def set_auth_token(self, target_token):   # but wait until "connected" !
        self._blynk._bridge_write( [str(self._pin),  "i", target_token])
        
    #   - write()s from here get bridged via server to other HW controller
    # only single value outgoing, no multi parameter list
    
    def digital_write(self, target_gpiopin, val):
        self._blynk._bridge_write( [str(self._pin),  "dw", target_gpiopin, val])
        
    def analog_write(self, target_pin, val):
        self._blynk._bridge_write( [str(self._pin),  "aw", target_pin, val])
        
    def virtual_write(self, target_vpin, val):
        self._blynk._bridge_write( [str(self._pin),  "vw", target_vpin, val])

    
    
    
class Blynk:
    def __init__(self, token, server='blynk-cloud.com', port=None, connect=True):
        self._vr_pins = {}
        self._do_connect = False
        self._on_connect = None
        self._on_disconnect = None
        self._on_setup = None
        self._on_tick = None
        self._tick_scale = 40
        self._tick_count = 0
        self._tick_state = None
        self.lock = threading.Lock()
        self._token = token
        if isinstance(self._token, str):
            self._token = str.encode(token)
        self._server = server
        if port is None:
                port = 8442
        self._port = port
        self._do_connect = connect
        self._digital_hw_pins = {}
        self._analog_hw_pins = {}
        self.user_tasks = []
        self.state = DISCONNECTED
        self._failed_pings = 0

    def idle_loop (self, start, delay): 
        # 200 Hz loop
        if self._on_tick: 
            self._tick_count = 1 + self._tick_count
            if self._tick_count == self._tick_scale:
                self._tick_count = 0
                rtn=self._on_tick(self._tick_state)
                if rtn != None:
                    self._tick_state = rtn
        while (now_in_ms()-start) < delay:
            pass
        return start + delay

    def _format_msg(self, msg_type, *args):
        if python_version == 2:
            data = bytes('\0'.join(map(str, args)))
        else:
            data = bytes('\0'.join(map(str, args)), 'ascii') 
        return struct.pack(HDR_FMT, msg_type, self._new_msg_id(), len(data)) + data

    def _handle_hw(self, data):
        if python_version == 2:
            params = list(data.split(b'\0')) 
        else:
            params = list(map(lambda x: x.decode('ascii'), data.split(b'\0'))) 
        cmd = params.pop(0)
        #logging.getLogger().debug("command: {}".format(cmd))
        if cmd == 'info':
            pass
        elif cmd == 'pm':
            pairs = zip(params[0::2], params[1::2])
            for (pin, mode) in pairs:
                pin = int(pin)
                if self._on_setup:
                    self._on_setup(pin, mode)
                if mode != 'in' and mode != 'out' and mode != 'pu' and mode != 'pd':
                    raise ValueError("Unknown pin %d mode: %s" % (pin, mode))
                #logging.getLogger().debug("pm: pin: {}, mode: {}".format(pin, mode))
            self._pins_configured = True
        elif cmd == 'vw':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].write:
                self._vr_pins[pin].write(params, pin, self._vr_pins[pin].state)
            else:
                logging.getLogger().warn("Warning: Virtual write to unregistered pin %d" % pin)
        elif cmd == 'vr':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].read:
                val = self._vr_pins[pin].read(pin, self._vr_pins[pin].state)
                if val != None : 
                    self.virtual_write(pin, val)
            else:
                logging.getLogger().warn("Warning: Virtual read from unregistered pin %d" % pin)
        elif self._pins_configured:
            if cmd == 'dw':
                pin = int(params.pop(0))
                val = int(params.pop(0))
                if pin in self._digital_hw_pins:
                    if self._digital_hw_pins[pin].write is not None:
                        self._digital_hw_pins[pin].write(val, pin, self._digital_hw_pins[pin].state)
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no digital 'write' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for digital write".format(pin))

            elif cmd == 'aw':
                pin = int(params.pop(0))
                val = int(params.pop(0))
                if pin in self._analog_hw_pins:
                    if self._analog_hw_pins[pin].write is not None:
                        self._analog_hw_pins[pin].write(val, pin, self._analog_hw_pins[pin].state)
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no analog 'write' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for analog write".format(pin))

            elif cmd == 'dr':
                pin = int(params.pop(0))
                if pin in self._digital_hw_pins:
                    if self._digital_hw_pins[pin].read is not None:
                        val = self._digital_hw_pins[pin].read(pin, self._digital_hw_pins[pin].state)
                        if val != None:   
                            self._send(self._format_msg(MSG_HW, 'dw', pin, val))
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no digital 'read' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for digital read".format(pin))

            elif cmd == 'ar':
                pin = int(params.pop(0))
                if pin in self._analog_hw_pins:
                    if self._analog_hw_pins[pin].read is not None:
                        val = self._analog_hw_pins[pin].read(pin, self._analog_hw_pins[pin].state)
                        self._send(self._format_msg(MSG_HW, 'aw', pin, val))
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no analog 'read' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for analog read".format(pin))
            else:
                raise ValueError("Unknown message cmd: %s" % cmd)

    def _new_msg_id(self):
        self._msg_id += 1
        if (self._msg_id > 0xFFFF):
            self._msg_id = 1
        return self._msg_id

    def _settimeout(self, timeout):
        if timeout != self._timeout:
            self._timeout = timeout
            self.conn.settimeout(timeout)

    def _recv(self, length, timeout=0):

        self._settimeout(timeout)
        try:
            self._rx_data += self.conn.recv(length)
        except socket.timeout:
            logging.getLogger().debug("socket timeout")
            return b''
        except socket.error as e:
            if e.args[0] == EAGAIN:
                return b''
            else:
                logging.getLogger().debug("RX Error")
                self._must_close = True
                return b''
        if len(self._rx_data) >= length:
            data = self._rx_data[:length]
            self._rx_data = self._rx_data[length:]
            return data
        else:
            return b''

    def _sendL(self, data, send_anyway):  # locked
        if self._tx_count < MAX_MSG_PER_SEC or send_anyway:
            retries = 0
            while retries <= MAX_TX_RETRIES:
                try:
                    self.conn.send(data)
                    self._tx_count += 1
                    break
                except socket.error as er:
                    if er.args[0] != EAGAIN:
                        logging.getLogger().debug(er)
                        return False
                    else:
                        time.sleep_ms(RE_TX_DELAY)
                        retries += 1
                        logging.getLogger().debug("retries ", retries)
            return True

    def _send(self, data, send_anyway=False):
        self.lock.acquire()  # lock against reentrancy
        was_sent = self._sendL(data, send_anyway)
        self.lock.release()
        if not was_sent:
            logging.getLogger().debug("Send Error")
            self._must_close = True
        
    def _close(self, emsg=None):
        self.conn.close()
        self._rx_data = b''
        self._failed_pings = 0   
        if emsg:
            logging.getLogger().error('%s, [closed]' % emsg)
        if self.state == AUTHENTICATED: 
            if self._on_disconnect:
                self._on_disconnect()
        self.state = DISCONNECTED
        time.sleep(RECONNECT_DELAY)

    def _server_alive(self):
        c_time = int(time.time())
        if self._m_time != c_time: # 1/sec
            self._m_time = c_time
            self._tx_count = 0
            
            if self._last_hb_id != 0 and (c_time - self._hb_time) > 3: 
                logging.getLogger().debug("HB waiting: "+str(c_time - self._hb_time))
                
            if c_time - self._hb_time >= HB_PERIOD and self.state == AUTHENTICATED:
                # time to issue another heartbeat ping
                if self._last_hb_id != 0:    
                    self._failed_pings += 1
                    logging.getLogger().debug("PING unanswered" + str(self._failed_pings))
                    if self._failed_pings > 1:  # 2 strikes & y're OUT
                        return False
                self._hb_time = c_time
                self._last_hb_id = self._new_msg_id()
                self._send(struct.pack(HDR_FMT, MSG_PING, self._last_hb_id, 0), True)
                #logging.getLogger().debug("PING out")
        return True


#    def _server_alive(self):
#        c_time = int(time.time())
#        if self._m_time != c_time:
#            self._m_time = c_time
#            self._tx_count = 0
#            if self._last_hb_id != 0 and c_time - self._hb_time > (MAX_SOCK_TO): 
#                return False
#            if c_time - self._hb_time >= HB_PERIOD and self.state == AUTHENTICATED:
#                self._hb_time = c_time
#                self._last_hb_id = self._new_msg_id()
#                self._send(struct.pack(HDR_FMT, MSG_PING, self._last_hb_id, 0), True)
#                #logging.getLogger().debug("hb ping")
#        return True


    def notify(self, msg):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_NOTIFY, msg))

    def tweet(self, msg):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_TWEET, msg))

    def email(self, to, subject, body):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_EMAIL, to, subject, body))

    def virtual_write(self, pin, val):
        if self.state == AUTHENTICATED:
            if type(val) == type([]):  
                if python_version == 2:
                    val = bytes('\0'.join(map(str, val)))
                else:
                    val = '\0'.join(map(str, val)) 
            self._send(self._format_msg(MSG_HW, 'vw', pin, val))

    def set_property(self, pin, prop, val):
        if self.state == AUTHENTICATED:
            if type(val) == type([]):  
                if python_version == 2:
                    val = bytes('\0'.join(map(str, val)))
                else:
                    val = '\0'.join(map(str, val))  
            self._send(self._format_msg(MSG_PROPERTY,  pin, prop, val))

    def _bridge_write(self, val):
        if self.state == AUTHENTICATED:
            if type(val) == type([]):             
                if python_version == 2:
                    val = bytes('\0'.join(map(str, val)))
                else:
                    val = '\0'.join(map(str, val))  
            self._send(self._format_msg(MSG_BRIDGE,  val))

    def sync_all(self):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC))

    def sync_virtual(self, pin):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC, 'vr', pin))

    def add_virtual_pin(self, pin, read=None, write=None, initial_state=None):
        if isinstance(pin, int) and pin in range(0, MAX_VIRTUAL_PINS):
            self._vr_pins[pin] = VrPin(read=read, write=write, blynk_ref=self, initial_state=initial_state)
        else:
            raise ValueError('the pin must be an integer between 0 and %d' % (MAX_VIRTUAL_PINS - 1))

    def add_digital_hw_pin(self, pin, read=None, write=None, inital_state=None):
        """
        add a callback for a hw defined pin for digital input/output.
        :param pin: pin number
        :param read: called when a value should be read from the hardware.
                     Depending upon how it is setup in the blynk app, will depend
                     upon whether this is reading a digital or analog value
        :param write: called when a value should be written to the hardware.
                        Depending upon how it is setup in the blynk app, will determine
                        if this is wring a digital or analog value.

        :return: None
        """
        if isinstance(pin, int):
            self._digital_hw_pins[pin] = HwPin(read=read, write=write, blynk_ref=self, initial_state=inital_state)
        else:
            raise ValueError("pin value must be an integer value")

    def add_analog_hw_pin(self, pin, read=None, write=None, initial_state=None):
        """
        add a callback for a hw defined pin for analog input/output.
        :param pin: pin number
        :param read: called when a value should be read from the hardware.
                     Depending upon how it is setup in the blynk app, will depend
                     upon whether this is reading a digital or analog value
        :param write: called when a value should be written to the hardware.
                        Depending upon how it is setup in the blynk app, will determine
                        if this is wring a digital or analog value.

        :return: None
        """
        if isinstance(pin, int):
            self._analog_hw_pins[pin] = HwPin(read=read, write=write, blynk_ref=self, initial_state=initial_state)
        else:
            raise ValueError("pin value must be an integer value")
            
    def gpio_auto(self, pull = None):
        import gpiozero as GPIO
        
        def gpioRead_h(pin, gpioObj):  
            v = gpioObj.value
            return (1 if v else 0)

        def gpioOut_h(val, pin, gpioObj): 
            gpioObj.value = val

        def setup_cb(pin,mode):
            # do gpio setup 
            if mode == "out":
                led = GPIO.LED(pin)
                self.add_digital_hw_pin(pin, None, gpioOut_h, led)
                logging.getLogger().debug(str(pin)+ str(mode))
                
            if mode == "in":
                print(pull)
                if pull=="up":
                    button = GPIO.DigitalInputDevice(pin, pullup=True) 
                elif pull=="down":
                    button = GPIO.DigitalInputDevice(pin, pullup=False) 
                elif pull=="button":
                    button = GPIO.Button(pin) 
                else:
                    button = GPIO.InputDevice(pin) 

                self.add_digital_hw_pin(pin, gpioRead_h, None, button)  
                # note the gpiozero button / led objects are payload as "state"
                logging.getLogger().debug(str(pin)+ str(mode))
            
        self._on_setup=setup_cb


    def on_connect(self, func):
        self._on_connect = func
        
    def on_disconnect(self, func):
        self._on_disconnect = func
        
    def Ticker(self, func, divider = None, initial_state = None):
        if divider:
            self._tick_scale = divider
        self._on_tick = func
        self._tick_state = initial_state

    def add_Task(self, second_period, task, initial_state=None, always = False):
        ut = UserTask(task, second_period, self, initial_state, always)
        self.user_tasks.append(ut)

    def Timer(self, task, time_secs, initial_state=None):
        tm = UserTimer(time_secs, task, self, initial_state)
        tm.arm()
        
    def lcd_widget(self, pin):
        lcdw = LCD(self, pin)
        self.add_virtual_pin(pin)
        return lcdw

    def gps_widget(self, pin):
        gpsw = GPS(pin)
        self.add_virtual_pin(pin, None, gpsw._virtual_write_incoming)
        return gpsw
        
    def accel_widget(self, pin):
        axlw = ACCEL( pin)
        self.add_virtual_pin(pin, None, axlw._virtual_write_incoming)
        return axlw
        
    def sensor_widget(self, pin):
        sensw = SENSOR( pin)
        self.add_virtual_pin(pin, None, sensw._virtual_write_incoming)
        return sensw

    def bridge_widget(self, pin):
        brw = BRIDGE(self, pin)
        self.add_virtual_pin(pin)
        return brw

    def connect(self):
        self._do_connect = True

    def disconnect(self):
        self._do_connect = False

    def run(self):

        #Run the Blynk client (blocking mode)

        self._start_time = now_in_ms()
        self._task_millis = self._start_time # nyi
        self._rx_data = b''
        self._msg_id = 1
        self._pins_configured = False
        self._timeout = None
        self._tx_count = 0
        self._m_time = 0
        self._must_close = False
        
        # start all of the tasks, which will be blocked on the
        # state going to AUTHENTICATED
        for task in self.user_tasks:
            task.run_task()

        while True:  # loop forever
            self._must_close = False
            while self.state != AUTHENTICATED:
                if self._do_connect:
                    try:
                        self.state = CONNECTING
                        logging.getLogger().debug('TCP: Connecting to %s:%d' % (self._server, self._port))
                        self.conn = socket.socket()
                        self.conn.connect(socket.getaddrinfo(self._server, self._port)[0][4])
                    except:
                        self._close('Fail to connect')
                        continue


                    self.state = AUTHENTICATING
                    hdr = struct.pack(HDR_FMT, MSG_LOGIN, self._new_msg_id(), len(self._token))
                    logging.getLogger().debug('Blynk connection successful, authenticating...')
                    self._send(hdr + self._token, True)
                    data = self._recv(HDR_LEN, timeout=MAX_SOCK_TO)
                    if not data:
                        self._close('Authentication t/o')
                        continue

                    msg_type, msg_id, status = struct.unpack(HDR_FMT, data)
                    if status != STA_SUCCESS or msg_id == 0:
                        self._close('Authentication fail')
                        continue

                    self.state = AUTHENTICATED
                    self._send(self._format_msg(MSG_HW_INFO, "h-beat", HB_PERIOD, 'dev', 'RPi', "cpu", "BCM2835"))
                    logging.getLogger().debug('Access granted.')
                    if self._on_connect:
                        self._on_connect()
                    self._start_time = now_in_ms()  
                else:
                    self._start_time = self.idle_loop(self._start_time, TASK_PERIOD_RES)

            self._hb_time = 0
            self._last_hb_id = 0
            self._tx_count = 0
            self._must_close = False
            while self._do_connect:
                data = self._recv(HDR_LEN, NON_BLK_SOCK)
                if data:
                    msg_type, msg_id, msg_len = struct.unpack(HDR_FMT, data)
                    if msg_id == 0:
                        pass
                        #logging.getLogger().debug('id=0 '+str(msg_id)+" "+str(msg_type)+" "+str(msg_len))
                        #self._close('invalid msg id %d' % msg_id) 
                        #break
                        # ... https://github.com/blynkkk/blynkkk.github.io/blob/master/BlynkProtocol.md
                        # ... advises disconnect() or stop for id==0 
                        # ... This appears empirically to be unnecessary. We choose to ignore.
                        # ... Seems to be no payload following, but so what?
                    if msg_type == MSG_RSP:
                        #logging.getLogger().debug("RSP in")
                        if msg_id == self._last_hb_id:
                            self._last_hb_id = 0
                            self._failed_pings = 0   
                    elif msg_type == MSG_PING:
                        #logging.getLogger().debug("PING in")
                        self._send(struct.pack(HDR_FMT, MSG_RSP, msg_id, STA_SUCCESS), True)
                    elif msg_type == MSG_HW or msg_type == MSG_BRIDGE:
                        data = self._recv(msg_len, MIN_SOCK_TO)
                        if data:

                            self._handle_hw(data)
                    else:
                        self._close('unknown message type %d' % msg_type)
                        break
                else:
                    self._start_time = self.idle_loop(self._start_time, IDLE_TIME_MS)
                if not self._server_alive():
                    self._close('Server offline, not responding')
                    break
                if self._must_close:
                    self._close('Network error')
                    break
                    


            if not self._do_connect:
                self._close()
                logging.getLogger().debug('Blynk disconnection requested by the user')


