
import gpiozero as GPIO

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)




# PWM

# generic gpio read by POLL from app
def gpioRead_h(pin, gpioObj):  
    v = gpioObj.value
    if type(v) == type(True):  # on/off gpio
        return (1 if v else 0)
    else:                      # gpio led pwm
        return v

def gpioOutPwm_h(val, pin, gpioObj):  # generic pwm write scaled 0-100 
    gpioObj.value = int(val[0])/100.0   # gpiozero pwm uses 0.0- 1.0

ledB = GPIO.PWMLED(16)        # blue led  controlled from 0-100 slider at app 
blynk.add_virtual_pin(8, None, gpioOutPwm_h, ledB)

# ... and the blue PWMLED pwm value is read & sent back to gauge on vpin 9 (0.0 -1.0)
blynk.add_virtual_pin(9, gpioRead_h, None, ledB)

#------------------------------

def cnct_cb():
    print ("Connected: ")

blynk.on_connect(cnct_cb)



######################################################################################

blynk.run()

######################################################################################
# AT APP:
# slider (H or V) to Vpin 8. Set to write at end of each slide action. Scaled 0-100 (think "percent")
# gauge polling Vpin 9.  Scaled 0-1.   (pigpio scales pwm 0.0 - 1.0)

# At RPI:
# LED on gpio 16
