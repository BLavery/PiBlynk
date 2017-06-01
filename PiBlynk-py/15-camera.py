# SIMPLE camera function. 

import picamera
import time
import os


from PiBlynk import Blynk
from mytoken import token
blynk = Blynk(token)

def timeNow():
    return time.asctime()[11:19].replace(":", ".")

imageDir = "images"
if not os.path.exists(imageDir):
    os.makedirs(imageDir)
    
def CamShot(imageName) :  
    iName = imageDir+"/"+imageName+".jpg" 
    try:   
        cam = picamera.PiCamera()

        # set any camera options needed:
        cam.vflip=True
        cam.hflip=True
        #cam.brightness=50

        cam.capture(iName)
        cam.close()
        return imageName
    except:
        return "CAM FAIL"
# reasons for "CAM FAIL":
#   RPi config not enabling camera
#   cam not installed OK
#   images folder missing

# rpi camera still-shot, from APP button on V26, and pic id returned on V27
def camButton_cb(val, pin, st) :
    if (val[0] == '1'):    # button press
        fname = "RPi-"+timeNow()  #proposed image name
        fname = CamShot(fname)  # name may be changed on error
        print(fname)
        blynk.virtual_write(27,fname)
blynk.add_virtual_pin(26, write=camButton_cb)

def cnct_cb():
    print ("Connected: "+ timeNow())
blynk.on_connect(cnct_cb)

######################################################################################

blynk.run()

######################################################################################

# http://picamera.readthedocs.io/en/release-1.10/index.html
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md

#----------------------------------

# At APP: 
# Button to Vpin 26. Momentary, not staydown action
# Value Display Vpin 27 in listen-only mode (no timer) for confirmed shot filename or error message


