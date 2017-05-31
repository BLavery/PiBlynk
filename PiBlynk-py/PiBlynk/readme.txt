
# BL  PiBlynk   V 0.3.5  28/5/17

# Python based Blynk library for Raspberry Pi



Creating a blynk object
-----------------------


import PiBlynk
blynk = PiBlynk.Blynk('your AUTH token here')
      - connection is TCP (no ssl option)

At this point an instance is created, but it has **not** tried to connect to the Blynk cloud. 
That is done with blynk.run(), which needs to be last line of script.
 
GPIO - zero coding
------------------

blynk.gpio_auto(pull)   
    pull = "up" or "down" or "button" or nothing will set pullup/down resistors (for ALL inputs used)
    "button" is gpiozero button object, resistor pullup
Imports gpiozero library to auto-configure any GPIO pins set as "digitalpin" at APP,
and to read (poll from APP) or write (APP to RPi) without further coding.
Note that in many practical cases this will not be adequate, and custom coding is needed instead, as below.
Note also that without this user call, no gpio functions are included in the library.


GPIO & Virtual Read & Write Callbacks
-------------------------------------


The callbacks are like this, and should be def'd before doing the add_xxx_pin():

def digital_read_callback(pin, state):
    digital_value = xxx       # access your hardware
    return digital_value  -  or None (and then your own code should do the wanted write()   
           but the "correct" way is to "return" the value to APP 
    
def digital_write_callback(value, pin, state):
    # access the necessary digital output and write the value
    return    

def analog_read_callback(pin, state):
    analog_value = 3.14159       # access your hardware
    return analog_value    
    
def analog_write_callback(value, pin, state):
    # access the nccessary analog output and write the value
    return
    
def virtual_read_callback(pin, state):
    virtual_value = 'Anything'       # access your hardware
    return virtual_value         return may be None, or a single value, or a list of values (eg for LCD)
           if using return None, then arrange own write back to APP,
           but the "correct" way is to "return" the value to APP 
            
def virtual_write_callback(value, pin, state):
    NOTE: "value" is a LIST, so you need to unpack eg value[0] etc
    # access the necessary virtual output and write the value
    return
    
blynk.add_digital_hw_pin(pin=pin_number, read=digital_read_callback, inital_state=None)
blynk.add_digital_hw_pin(pin=pin_number, write=digital_write_callback, inital_state=None)
blynk.add_analog_hw_pin(pin=pin_number, read=analog_read_callback, inital_state=None)
blynk.add_analog_hw_pin(vpin_number, write=analog_write_callback, inital_state=None)
blynk.add_virtual_pin(vpin_number, read=virtual_read_callback, inital_state=None)
blynk.add_virtual_pin(vpin_number, write=virtual_write_callback, inital_state=None)
    in this context, write means "APP writes to HW" and read is "APP polls HW expecting HW reply"

initial_state is an optional payload of one value 
    That one value may possibly be a LIST of values if you want to pass several
gpio and analog pins are actual GPIO pin numbers (BCM for RPi)
virtual pins are 0 - 127

User Timers & Tasks:
--------------------

It is also possible to set up timed user tasks.  
These functions ("callbacks") will be called based on the period or time specified 
    instead of any particular Blynk Application interaction.
Timer & Task times are fractional in seconds

1. Timer is a 1-shot timed function - callback runs concurrent with blynk
    A Timer may be created ad-hoc any time, and is start()'ed/arm()'ed immediately.
    Timed callback will trigger independent of "up" status (unlike task).
2. Task is a repeating function - callback runs concurrent with blynk
    Tasks are registered in the user script above blynk.run(), 
       and are all start()'ed by the run() function.
    By default, callback triggering at each timing will occur only if communications with server is "up", 
          and it will "miss its turn" otherwise.  
    If the option "always" == True, callbacks trigger each time, irrespective of network status.
3. Ticker is a repeating function - callback suspends blynk until its return
    Register and start (one only) simple "ticker" function callback.
    "divider" (default 40) divides into 200 to give ticker frequency. eg divider 100 gives 2 ticks / sec.
    Unlike Task & Timer, Ticker is not threaded/concurrent, and should exit promptly to not hold up blynk.
    (eg 3 mSec would be considered quite too long.)

def timer_callback(state):
    # do anything you like
    return
    
blynk.Timer(time_secs, timer_callback, state)    
    
def task_callback(initial_state):
    # do anything you like
    return new_state      or just return

blynk.add_Task(period_seconds, task_callback, initial_state=None, always=False)
      
def ticker_callback(state):
    # do anything you like
    return new_state   or just return

blynk.Ticker(ticker_callback, divider=40, initial_state = None, always=False)
blynk.Ticker(None) - disables
    

Software widgets at python end:
-------------------------------

mylcd = blynk.lcd_widget(vpin_number)
   mylcd.cls()
   mylcd.Print(x, y, message)   x=0-15   y=0-1
   
myGPS = blynk.gps_widget(vpin_number)
   myGPS.lat   in degrees
   myGPS.lon
   myGPS.timestamp   ie last update time from APP
   myGPS.set_ref() or set_ref(lat0, lon0)
   myGPS.distance()   in km
   myGPS.direction()    compass bearing from start

   
myAccel = blynk.accel_widget(vpin_number)
   myAccel.x   in m/s/s
   myAccel.y
   myAccel.z
   myAccel.timestamp
   myAccel.pitch()
   myAccel.roll()
   
mysensor = blynk.sensor_widget(vpin_number)   good for light or proximity, but anything you want 
 to buffer the info for.
   mysensor.value
   mysensor.timestamp

bridge = blynk.bridge_widget(my_vpin_number)   - all writes to this widget get bridged to other HW
   bridge.set_auth_token(target_token)  - but first wait until "connected" !
   bridge.virtual_write(target_vpin, val)   val = single param only, no lists
   bridge.digital_write(target_gpiopin, val) 


blynk.notify(message_text)
blyk.email([to,] subject, body)
blynk.tweet(message_text)
blynk.virtual_write(vpin_number, value)   value = either single value (int/str) or list of values.
       For ad-hoc writing to a vpin (ie toward APP),
       without necessarily having done add_virtual_pin()
blynk.set_property(vpin, property, value)    eg "color", "#ED9D00"    or "label"/"labels" "onLabel" etc
blynk.on_connect(connect_callback)
blynk.on_disconnect(disconnect_callback)
blynk.connect()
blynk.disconnect()

blynk.run()   -  the main non-returning loop of the blynk engine.  Last line of python script.

Example files 
-------------
01-simplest-gpio.py
02-custom-gpio.py
05-rlogger.py
06-jlogger2oled.py
07-pir.py
08 misc.py
09-ticker.py
10-lcd.py
11-accel.py
12-gps.py
13-pwm.py
14-terminals.py
15-camera.py
16-camera-preview
31-bridge-out.py
32-bridge-in.py
40-email.py
99-ALL.py
