# This example is designed to be paired with example file 32-bridge-in.py
# Run the two with DIFFERENT DEVICE TOKENS.
# (They can be either in same "project" or separate projects as set at phone. Just use different tokens.)


# This "out" bridge speaks (via server) to other "in" device.
# It repeatedly sends OUR time to other RPi for display there,
# and uses our Button4 (our gpio 19) to display on the other RPi's GPIO 21.



# 1. Create bridge widget 
# 2. After getting connected to server, register other end's token
# 3. Send virtual & digital commands to other RPi

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#----------------------------------

bridge_to_otherpi = blynk.bridge_widget(40)   # using our vpin 40 as our outgoing channel

#------------------------------------
# our button -> their LED 
our_button4 = GPIO.Button(19) 
other_rpi_redled_gpio = 21
our_button4.when_pressed = lambda :  bridge_to_otherpi.digital_write(other_rpi_redled_gpio, 1)    
our_button4.when_released = lambda : bridge_to_otherpi.digital_write(other_rpi_redled_gpio, 0) 


#----------------------------------
# Our time/hostname to their LCD
def timer2loop(s):  # 2 sec repeat timer

    bridge_to_otherpi.virtual_write(61, timeNow()+" " +socket.gethostname())
    # write OUR time & hostname to other RPI on its V61
    print("out ->61 time ")

blynk.add_Task(2, timer2loop)

#----------------------------


def cnct_cb():
    print ("Connected: "+ timeNow())
    
    # things that should wait until "connected":
    bridge_to_otherpi.set_auth_token(token2)   # register token of "other" bridged device
blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################

# At APP:
# nothing exc bridge widget, no settings
