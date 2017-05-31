
import os

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

is_rpi3 = len(os.popen("cat /proc/cpuinfo | grep ARMv7 > /dev/zero && echo $?").read()) == 2

# Use V30 button to control the PCB activity LED - RPI3 only !!
# Instead of showing SD card activity, it blinks regularly
# We use Ticker to do the flashing.

if is_rpi3:
    def ACTLED_cb( val, pin, st):
        if int(val[0]) > 0: 
            blynk.Ticker(ACTLED_toggle, 70, False)  # 1.5 Hz
        else :
            blynk.Ticker(None)
            os.popen('sudo sh -c "echo mmc0 > /sys/class/leds/led0/trigger"')
            # back to normal

    blynk.add_virtual_pin(30, write=ACTLED_cb)

    def ACTLED_toggle(ACTLED_on):
        if (ACTLED_on):
            os.popen('sudo sh -c "echo none > /sys/class/leds/led0/trigger"')
        else:
            os.popen('sudo sh -c "echo default-on > /sys/class/leds/led0/trigger" ')
        return not ACTLED_on
# RPI2 and RPIzero are different from RPI3.  
# See https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
else:
    print("Not RPI3")
    
def cnct_cb():
    print ("Connected: "+ timeNow())

blynk.on_connect(cnct_cb)


######################################################################################

blynk.run()

######################################################################################

# At APP:
# Button widget to V39, values 0 - 1
