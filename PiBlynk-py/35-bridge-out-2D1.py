# This example is designed to be paired with D1 Mini ESP8266
# Run the two with DIFFERENT DEVICE TOKENS.
# (They can be either in same "project" or separate projects as set at phone. Just use different tokens.)


# This "out" bridge speaks (via server) to other "in" device.
# It repeatedly uses our Button4 (our gpio 19) to display on the D1's GPIO 4.



# 1. Create bridge widget 
# 2. After getting connected to server, register other end's token
# 3. Send digital commands to D1

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)
import gpiozero as GPIO

#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#----------------------------------

bridge_to_D1 = blynk.bridge_widget(40)   # using our vpin 40 as our outgoing channel

#------------------------------------
# our button -> their LED 
our_button4 = GPIO.Button(19) 
D1_blueled_gpio = 4
our_button4.when_pressed = lambda :  bridge_to_D1.digital_write(D1_blueled_gpio, 1)    
our_button4.when_released = lambda : bridge_to_D1.digital_write(D1_blueled_gpio, 0) 

#-----------------------------------

ourLed = GPIO.LED(20)

# and D1 will send back a message to our vp65 on each D1 LED change (which we caused!).
def xxx_h(value, pin, st):
    print("incoming: ", value[0])
    ourLed.value = int(value[0][4])  # so we turn on OUR led too!
    
blynk.add_virtual_pin(65, None, xxx_h)

#----------------------------


def cnct_cb():
    print ("Connected: "+ timeNow())
    
    # things that should wait until "connected":
    bridge_to_D1.set_auth_token(token4)   # register token of "other" bridged device
blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################


