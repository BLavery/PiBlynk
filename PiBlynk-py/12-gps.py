
# iPhone blynk may not have GPS widget?

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]


gps = blynk.gps_widget(11)

# write back computed GPS distance when POLLED by app 

def distRead_h(pin, st): 
    mins=""
    if gps.timestamp:
        mins = round((time.time() - gps.timestamp)/60)
        print(mins)
        mins = "["+str(mins)+"]" if mins> 4 else ""
        
    return "GPS Dist " + str(int(gps.distance())) +" m " + str(int(gps.direction())) + " deg "+mins
blynk.add_virtual_pin(12, read=distRead_h)


#-------------------------

# a 2 second task loop:




def timer2loop(s):  # 2 sec repeat timer

    print(gps.lat, gps.lon, gps.distance(), gps.direction())
    print(round(gps.distance()), "m ")


blynk.add_Task(2, timer2loop)

#----------------------------


def cnct_cb():
    print ("Connected: "+ timeNow())

blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################

# At APP:
# GPS widget, to Vpin 11
# Value Display Vpin 12, polling 2 sec
