
# Automatically sets any GPIO writes from APP as LED,  and all GPIO reads (poll) from APP as BUTTON

import gpiozero as GPIO


from PiBlynk import Blynk
from mytoken import token
blynk = Blynk(token)


def cnct_cb():
    print ("Connected: ")
blynk.on_connect(cnct_cb)


blynk.gpio_auto("button")


######################################################################################

blynk.run()

######################################################################################


# at APP:
# 3 buttons writing to GPIOs 21, 20, 16 (leds on rpi)
# 3 LEDs polling gpios 6, 26  19 (rpi buttons) and 14 (rpi pir)


