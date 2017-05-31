
from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]



lcd = blynk.lcd_widget(33)
def timer2loop(s):  # 2 sec repeat timer
        
    # write time message to LCD at APP on V33
    print("lcd")
    #lcd.cls()
    lcd.Print(0,0,timeNow())
    lcd.Print(0,1,"RPI")
blynk.add_Task(2, timer2loop)


######################################################################################

blynk.run()

######################################################################################

# AT APP:
# LCD widget listening to V33
