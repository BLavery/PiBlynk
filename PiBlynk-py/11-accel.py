
from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

axl = blynk.accel_widget(17)

def timer2loop(s):  # 2 sec repeat timer
    #print(axl.z, "z")
    print(int(axl.pitch()), int(axl.roll()))

blynk.add_Task(2, timer2loop)

#----------------------------


def cnct_cb():
    print ("Connected: "+ timeNow())

blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################

# at APP:
# accelerometer widget, to VPin 17
