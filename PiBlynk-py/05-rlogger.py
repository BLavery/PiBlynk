

import socket

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#------------------------------------


# rlogger

rlctr = 0   
def timer3loop(s):  
    # write to (terminal style) rlogger at APP on vp 18
    global rlctr
    rlctr = rlctr+1
    blynk.virtual_write(18, timeNow()+ " "+str(rlctr) + "\n"); 

blynk.add_Task( 6, timer3loop)   # for every 6 secs


def cnct_cb():
    print ("Connected: "+ timeNow())
    blynk.virtual_write(18, "\n"+socket.gethostname()+"\n")
blynk.on_connect(cnct_cb)


######################################################################################

blynk.run()

######################################################################################


# At APP:
# make terminal widget on that V18, fill whole phone screen, 
# turn off its input box
# now it is a live-time remote log display screen rpi->app  with rlogger.write()
# but server WONT indefinitely buffer messages if APP is offline.

