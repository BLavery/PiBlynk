import gpiozero as GPIO

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)

import time
def timeNow():
    return time.asctime()[11:19]

def pir_release_cb():
    blynk.notify("PIR alert: " + timeNow())   # beep the smartphone
    print ("pir alert")
    
pir = GPIO.MotionSensor(14) 
pir.when_motion = pir_release_cb   # call this func when motion event fires

#-------------------------------------------

def cnct_cb():
    print ("Connected: ")
blynk.on_connect(cnct_cb)



blynk.run()

######################################################################################
# AT APP:
# simply a "notification" icon on screen

# At RPi:
# PIR at gpio 14
