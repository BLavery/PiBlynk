
# Camera function with (fixed) preview


import os


from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)

#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19].replace(":", ".")


#  CAMERA 
#  with optional preview to HDMI screen (but not to VNC screen!)

# http://picamera.readthedocs.io/en/release-1.10/index.html
# https://www.raspberrypi.org/documentation/usage/camera/python/README.md


import picamera


imageDir = "images"
if not os.path.exists(imageDir):
    os.makedirs(imageDir)
    
preview_time = 6  # in seconds.  0 = no preview
cambusy = False


def CamShot1(fname) :  
    global cambusy
    try:   
        cam = picamera.PiCamera()
    except:
        blynk.virtual_write(27,"CAM FAIL")
        cambusy = False
        print("CAM FAIL - camera installed OK?")
        return
        # possible reasons here for "CAM FAIL":
        #   RPi config not enabling camera
        #   cam not installed OK

    # set any camera options needed:
    cam.vflip=True
    cam.hflip=True
    #cam.resolution = (700,300) # 1024 x 768 default??????
    #cam.brightness=50

    if preview_time > 0:
        # show a preview to (real, not VNC) screen:
        cam.preview_fullscreen = False
        cam.preview_window = (200, 200, 600, 500)
        cam.start_preview() 
    blynk.Timer(preview_time + 0.1,  CamShot2_shoot, [cam,fname])
    # preview wait time is implemented with a Timer. (ie "to be resumed later!")


def CamShot2_shoot(param):
    global cambusy
    cam=param[0]
    fname = param[1]
    if preview_time >0:
        cam.stop_preview() # up to 0.9 sec
    try:
        cam.capture(imageDir+"/"+fname+".jpg")          # takes up to 2.5 sec 
        print(fname)

    except:
        fname = "CAM FAIL"
        print("CAM FAIL - no images folder?")

    cam.close()   # abt 0.7 sec
    blynk.virtual_write(27,fname)
    cambusy = False


# rpi camera still-shot, from APP button on V26, and pic id returned on V27

def camButton_cb(val, pin, st) :
    global fname, cambusy
    if (val[0] == '1'):    # button press
        if cambusy:
            blynk.virtual_write(27,"WAIT") 
        else:
            cambusy = True
            fname = "RPi-"+timeNow().replace(":", ".")  #proposed image name. NO COLONS!
            blynk.virtual_write(27,"Busy")
            CamShot1(fname)

blynk.add_virtual_pin(26, write=camButton_cb)


def cnct_cb():
    print ("Connected: ")

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


