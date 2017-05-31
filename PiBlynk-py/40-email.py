

import time


from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#------------------------------------

def cnct_cb():
    print ("Connected: "+ timeNow())
    
    blynk.email("themagician@gmayle.com", "subject 44", "Test.  Body")    ###<<<<<<<<<<<<<<<<<<<< FIX ME
    print("sent email via blynk server. nothing more to do in this demo. Exit!")
    time.sleep(3)
    exit()
blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################

# At APP:
# nothing except put an email widget to screen.
