


import os, socket
import gpiozero as GPIO
#  http://gpiozero.readthedocs.io/en/v1.3.1/index.html

#import logging
#logging.basicConfig(level=logging.CRITICAL)

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#------------------------------------

# Buttons or other inputs by manual coding. Direct GPIO (not Vpin) settings at app.
# Flexible. can make Button, InputDevice etc pulldown etc as desired.
# Slower latency

# generic gpio read by POLL from app

def gpioRead_h(pin, gpioObj):  
    v = gpioObj.value
    if type(v) == type(True):  # on/off gpio
        return (1 if v else 0)
    else:                      # gpio led pwm
        return v
    

# set up any buttons (or whatever) and connect to gpioRead_h
button1 = GPIO.Button(13)    
blynk.add_digital_hw_pin(13, gpioRead_h, None, button1)  # note the gpiozero button object is payload as "state"

#---------------------------------------------------

# easy-create for gpiozero Button in PUSH mode (vPin settings at app)
# faster response

def make_push_button_to_led(gpiopin, vpin):    
    # create a gpiozero button, and then on every press/release write to a vPin
    # good for pushing to a led widget (value 0 or 255) on app
    button = GPIO.Button(gpiopin) 
    button.when_pressed = lambda :  blynk.virtual_write(vpin, 255)    
    button.when_released = lambda :  blynk.virtual_write(vpin, 0)  

make_push_button_to_led(6, 2)  # ie button on gpio 6, push its changes to led widget vpin 2  B2
make_push_button_to_led(26, 3) # B3
make_push_button_to_led(19, 4) # B4

#-----------------------------

# generic gpio write   (GPIO settings at app)

def gpioOut_h(val, pin, gpioObj): 
    gpioObj.value = val

# set up the RPi LEDs or other outputs and connect to generic gpioOut
ledR = GPIO.LED(21)  # gpiozero led objects
ledG = GPIO.LED(20)
blynk.add_digital_hw_pin(21, None, gpioOut_h, ledR)
blynk.add_digital_hw_pin(20, None, gpioOut_h, ledG)

# keep blue led for pwm below

#------------------------------


# PWM

def gpioOutPwm_h(val, pin, gpioObj):  # generic pwm write scaled 0-100 
    gpioObj.value = int(val[0])/100.0   # gpiozero pwm uses 0.0- 1.0

ledB = GPIO.PWMLED(16)        # blue led  controlled from 0-100 slider at app 
blynk.add_virtual_pin(8, None, gpioOutPwm_h, ledB)

#---------------------------------

# ... and the blue PWMLED pwm value is read & sent back to gauge on vpin 9 (0.0 -1.0)
blynk.add_virtual_pin(9, gpioRead_h, None, ledB)

#------------------------------

# widgets at app

lcd = blynk.lcd_widget(33)
axl = blynk.accel_widget(17)
gps = blynk.gps_widget(11)
light = blynk.sensor_widget(25)

#-------------------------------

# terminal from APP into python interpreter
_last_cmd = ""
def pyterminal_h(value, pin, st):
        global _last_cmd
        cmd = value[0]
        if cmd == ".":
            cmd = _last_cmd
            blynk.virtual_write(pin, "> "+cmd+"\n")
        else:
            _last_cmd = cmd
        try:
            out = eval(cmd)
            if out != None:
                outstr = "= "+repr(out)
        except:
            try:
                exec(cmd)
                outstr = "= (OK)"
            except Exception as e:
                outstr = repr(e)
        blynk.virtual_write(pin, outstr+"\n")
        

blynk.add_virtual_pin(14, None, pyterminal_h)

#--------------------------------
# Terminal from APP into OS shell

def osterminal_h(value, pin, st):
        try:
            outstr = os.popen(value[0]).read()
        except Exception as e:
            outstr = repr(e)
        blynk.virtual_write(pin, outstr)

blynk.add_virtual_pin(13, None, osterminal_h)
# These "terminals" esp the OS one could be dangerous vulnerability. 
# Be sure you really, really want to keep this in regular installation !!!!
#--------------------------------

# a generic handler for incoming vpin writes from app.
# a placeholder until you code your own specific handlers
# (eg "light" has been done as a sensor_widget)

def virt_generic_h(val, pin, txt):  
    print(txt, val ,"\x1b[K\x1b[1A")

blynk.add_virtual_pin(24, None, virt_generic_h, "Prox: ") # text get a ride as "state"
blynk.add_virtual_pin(20, None, virt_generic_h, "js: ")

#-----------------------------------

# write back computed GPS distance when POLLED by app 

def distRead_h(pin, st):  
    mins=""
    d = gps.distance()*1000
    b = gps.direction()
    if gps.timestamp:
        mins = round((time.time() - gps.timestamp)/60)
        mins = "["+str(mins)+" min]" if mins>= 0  else ""
    #print("GPS ",d, b, mins,"\x1b[K\x1b[1A")
    
    if d>100:
        return "GPS " + str(int(d/100)/10) +" km  " + str(int(b)) + " dg  "+mins
    elif d > 40:  # very short dist = likely gps reading errors!
        return "GPS " + str(int(d)) +" m  " + str(int(b)) + " dg  "+mins
    else:
        return "GPS " + str(int(d)) +" m  " +mins
        
blynk.add_virtual_pin(12, read=distRead_h)

#---------------------------

# app polls for time value

def timeRead_h(pin, st):
    return timeNow()
blynk.add_virtual_pin(10, read=timeRead_h)    

#-------------------------------

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
        ## fail will also print certain camera messages to screen
        blynk.virtual_write(27,"CAM FAIL")
        cambusy = False
        print("CAM FAIL - camera installed?")
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


#-----------------


# rlogger

rlctr = 0   
def timer3loop(s):  
    # write to (terminal style) rlogger at APP on vp 18
    global rlctr
    rlctr = rlctr+1
    blynk.virtual_write(18, timeNow()+ " "+str(rlctr) + "\n"); 

blynk.add_Task(5, timer3loop)   # for every 5 secs

def rlogstart(st):
    blynk.virtual_write(18, "\n"+socket.gethostname()+"\n")
    #slight delay: allowing for blynk to get connected to server
    # actually, it would be cleaner to put this first message into the cnct_cb() at end of this script

blynk.Timer(3, rlogstart)   # this is a 1-shot, after 3 secs

#------------------------------------------

# NOTE: this crashes if oled library or oled hardware display not found !!!
# remove all oled lines if not using oled
try:
    from  oled96 import oled 
    oled.yell(" Hello")
except:
    print ("No oled")

def jlog(val, pin, st):
    if oled:
        oled.jnl(val[0])
    print(val[0])
blynk.add_virtual_pin(19, write= jlog)

#-------------------------

# a 2 second task loop:

# repeat timer to push some things to app
# 1. pulsing LED at app ("active" indicator)
# 2. message to LCD

# and to display some incoming widget data:
# accelerometer, gps and light sensor


#----------------------------------

# PIR to phone notification

def pir_release_cb():
    blynk.notify("PIR alert: " + timeNow())   # beep the smartphone
    print ("pir alert")
    
pir = GPIO.MotionSensor(14) 
pir.when_motion = pir_release_cb   # call this func when motion event fires

#-------------------------------------------


is_rpi3 = len(os.popen("cat /proc/cpuinfo | grep ARMv7 > /dev/zero && echo $?").read()) == 2

# Use V30 button to control the PCB activity LED - RPI3 only !!
# Instead of showing SD card activity, it blinks regularly
# We use Ticker to do the flashing.

if is_rpi3:
    def ACTLED_cb( val, pin, st):
        if int(val[0]) > 0: 
            blynk.Ticker(ACTLED_toggle, 70, False)  # 1.5 Hz
        else :
            blynk.Ticker(None)
            os.popen('sudo sh -c "echo mmc0 > /sys/class/leds/led0/trigger"')
            # back to normal

    blynk.add_virtual_pin(30, write=ACTLED_cb)

    def ACTLED_toggle(ACTLED_on):
        if (ACTLED_on):
            os.popen('sudo sh -c "echo none > /sys/class/leds/led0/trigger"')
        else:
            os.popen('sudo sh -c "echo default-on > /sys/class/leds/led0/trigger" ')
        return not ACTLED_on
# RPI2 and RPIzero are different from RPI3.  
# See https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi


#----------------------------------


def timer2loop(state):  # 2 sec repeat timer ("bright" is the initial-state/new-state payload)
    # job1: wink led widget at APP on V15
    bright = state[0]
    colr = state[1]
    blynk.virtual_write(15, bright)
    if bright == 0:
        blynk.set_property(15, "color", ["#00FF00", "#FF4444", "#4488FF"][colr] )
        colr = (1+colr) % 3
    bright = 255-bright

        
    # job2: write time message to LCD at APP on V33

    lcd.cls()
    lcd.Print(0,0,timeNow())
    lcd.Print(0,1,"RPi: "+socket.gethostname())

    # job3 show some stuff
    #print(axl.z, "z\x1b[K\x1b[1A")
    #print("pitch/roll: ",int(axl.pitch()), int(axl.roll()))
    #print(gps.lat, gps.lon)
    #print(round(gps.distance()), "m ")
    #print(light.value, "lx")

    return [bright, colr]  # we return amended "state"
    
blynk.add_Task(2, timer2loop, [0,0])  # we put brightness & colr 0 into initial_state param3

#----------------------------

def cnct_cb():
    print ("Connected: "+ timeNow())
blynk.on_connect(cnct_cb)


def discon_cb():
    print ("Disconnected: "+ timeNow())

blynk.on_disconnect(discon_cb)






######################################################################################

blynk.run()

######################################################################################

