
# manually configured GPIOs

import gpiozero as GPIO

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


######################################################################################

#  Button1 poll mode
# Buttons or other inputs by manual coding. Direct GPIO (not Vpin) settings at app.
# Flexible. can make Button, InputDevice etc pulldown etc as desired.
# Slower latency

# generic gpio read by POLL from app

def gpioRead_h(pin, gpioObj):  
    v = gpioObj.value
    if type(v) == type(True):  # on/off gpio
        return (1 if v else 0)
    else:                      # gpio led pwm
        return v
    

# set up any buttons (or whatever) and connect to gpioRead_h
button1 = GPIO.Button(13)    
blynk.add_digital_hw_pin(13, gpioRead_h, None, button1)  # note the gpiozero button object is payload as "state"

######################################################################################

# Buttons 2 3 4 - push mode
# easy-create for gpiozero Button in PUSH mode (vPin settings at app)
# faster response

def make_push_button_to_led(gpiopin, vpin):    
    # create a gpiozero button, and then on every press/release write to a vPin
    # good for pushing to a led widget (value 0 or 255) on app
    button = GPIO.Button(gpiopin) 
    button.when_pressed = lambda :  blynk.virtual_write(vpin, 255)    
    button.when_released = lambda :  blynk.virtual_write(vpin, 0)  

make_push_button_to_led(6, 2)  # ie button on gpio 6, push its changes to led widget vpin 2  B2
make_push_button_to_led(26, 3) # B3
make_push_button_to_led(19, 4) # B4

######################################################################################

# 3 LEDs:
def gpioOut_h(val, pin, gpioObj): # generic gpio write   (GPIO settings at app)
    gpioObj.value = val

# set up the RPi LEDs or other outputs and connect to generic gpioOut
ledR = GPIO.LED(21)  # gpiozero led objects
ledG = GPIO.LED(20)
ledB = GPIO.LED(16)
blynk.add_digital_hw_pin(21, None, gpioOut_h, ledR)
blynk.add_digital_hw_pin(20, None, gpioOut_h, ledG)
blynk.add_digital_hw_pin(16, None, gpioOut_h, ledB)


#------------------------------

def cnct_cb():
    print ("Connected: ")
blynk.on_connect(cnct_cb)




######################################################################################

blynk.run()

######################################################################################

# at APP:
# 3 buttons writing to GPIOs 21, 20, 16 (leds on rpi)
# 3 led widgets listening to gpios 6, 26  19 (rpi buttons) 
# one value display widget polling gpio 13 (rpi button)
