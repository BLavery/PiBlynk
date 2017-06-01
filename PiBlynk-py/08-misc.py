
from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]




# a generic handler for incoming vpin writes from app.
# a placeholder until you code your own specific handlers
# (eg "light" could been done as a sensor_widget)

def virt_generic_h(val, pin, txt):  
    print(txt, val)

blynk.add_virtual_pin(24, None, virt_generic_h, "Prox: ") # text get a ride as "state"
blynk.add_virtual_pin(20, None, virt_generic_h, "joystick: ")
blynk.add_virtual_pin(25, None, virt_generic_h, "Light: ")


#---------------------------

# app polls (V10) for time value

def timeRead_h(pin, st):
    return timeNow()
blynk.add_virtual_pin(10, read=timeRead_h)    

#---------------------------------


# a 2 second winking led at app - v15


bright=0 
def timer2loop(s):  # 2 sec repeat timer
    # job1: wink led widget at APP on V15
    global bright
    blynk.virtual_write(15, bright)
    bright = 255-bright


blynk.add_Task(2, timer2loop)

#----------------------------

def cnct_cb():
    print ("Connected: "+ timeNow())

blynk.on_connect(cnct_cb)




######################################################################################

blynk.run()

######################################################################################


# At APP:
# Joystick V20
# Proximity sensor V24
# Light sensor V25
# Value Display on V10, 2 sec requests

