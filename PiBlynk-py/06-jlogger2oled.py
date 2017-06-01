
from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]


#------------------------------------------

# NOTE: this crashes if oled library or oled hardware display not found !!!
# remove all oled lines if not using oled
from  oled96 import oled 
oled.yell(" Hello")

def jlog(val, pin, st):
    oled.jnl(val[0])
    print(val[0])
blynk.add_virtual_pin(19, write= jlog)




######################################################################################

blynk.run()

######################################################################################



# At RPI:
# oled on i2c   128x64 0x3c
# 
# At APP:
# Terminal widget on V19

