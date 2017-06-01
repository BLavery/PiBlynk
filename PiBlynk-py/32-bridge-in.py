# This example is designed to be paired with example file 31-bridge-out.py
# Run the two with DIFFERENT DEVICE TOKENS.
# (They can be either in same "project" or separate projects as set at phone. Just use different tokens.)


# This "in" bridge receives data directly from other RPi.
# Our display shows incoming messages.
# Our LED on gpio 21 is controlled by button at other end.


import gpiozero as GPIO

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token2)    # <<<<<<<<<<<<<<<<<<<<   USE DIFFERENT TOKED FROM OTHER END !!!

#-----------------------------------------------
# gpio (incoming) write  

def gpioOut_h(val, pin, gpioObj): 
    gpioObj.value = val   # control the LED
    print("Incoming GPIO OUT command:", pin, val)

# set up the RPi LED or other outputs and connect to generic gpioOut function above
ledR = GPIO.LED(21)  # gpiozero led objects
blynk.add_digital_hw_pin(21, None, gpioOut_h, ledR)

#-----------------------------------------
# Listen for anything coming in V61. Just print it
def virt_in_h(val, pin, st):  
    print("Incoming on VP:", pin, val)

blynk.add_virtual_pin(61, write=virt_in_h)   # we place a LISTEN for incoming writes on V61



def cnct_cb():
    print ("Connected: ")
    print("Waiting for incoming messages ...")
blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################

#At APP:
#    Nothing
