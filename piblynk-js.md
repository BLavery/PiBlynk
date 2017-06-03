# piblynk  
# javascript library for Blynk on Raspberry Pi 3

Will not run on V0.xx (0.10, 0,12) versions of nodejs, as on RPi raspbian.   
And I find that nodejs later versions (as at May 2017) do not execute on old CPU versions of RPi (armV6).

Therefore this library runs only on RPI3 (ie ARMv7), with upgraded nodejs (eg V6.x)

Derived from:  https://github.com/vshymanskyy/blynk-library-js
   MIT licence

Stripped of all non-RPi sections (eg espruino, browser)  
Several changes to improve connection stability.  
Added widgets at RPi end.

Dependencies:  
* the library itself needs: onoff  
* the example files use: rpio, my-local-ip, campi, oled-js-pi

## USAGE:

var Blynk = require("piblynk")      
var blink = new Blynk.Blynk(token [,options])  
    where options = {  
    heartbeat: 10000            10000msec default  
    connector: new Blynk.TcpClient()     or SslClient()  
    skip_connect: true         false default  
     }
 
blynk.on(event, func)   event = 'connect', 'disconnect'  
blynk.disconnect([reconnect])   reconnect defaults true  
blynk.connect()

blynk.virtualWrite(vpin, val)  
blynk.setProperty(vpin, property, val)    eg "color", "#23C48E"  (green)

var VP = new blynk.VirtualPin(vpin)  
   VP.write(value)  
   VP.setProperty(property, value)  
   VP.on("write", function(param){ ...})      
     ("write" means incoming data)  param is array: param[0], param[1] etc  
   VP.on("read", function(){ ...})  
     ("read" means req for data to be sent back)    
     function should include a VP.write() to respond with the data  


var lcd = new blynk.WidgetLCD(vPin)  
    lcd.clear()  
    lcd.print(x, y, msg)

var led = new blynk.WidgetLED(vPin)  
    led.setValue(cal)    0-255 
    led.turnOn()  
    led.turnOff()  
    led.setColour(val)   eg "#EEDD00"  

var axl = new blynk.WidgetAccel(vPin)  
    INCLUDE & SET WIDGET AT APP  
    axl.roll() 
    axl.pitch() 
    axl.X 
    axl.Y  
    axl.Z  
    axl.age()

var gps = new blynk.WidgetGPS(vPin)  
    INCLUDE & SET WIDGET AT APP  
    gps.latitude  
    gps.longtitude  
    gps.age()    seconds since last update  
    gps.distance()  
    gps.direction()  
    gps.reset()  
    
var light = new blynk.WidgetSensor(vPin)    Buffered sensor reading, single value (eg prox, light)  
    light.value  
    light.age()

var bridge = new blynk.WidgetBridge(my_vpin_number)  
    INCLUDE WIDGET AT APP  
    bridge.setAuthToken(target_token)  
    bridge.digitalWrite(target_gpio_pin, val)  
    bridge.analogWrite(target_analog_pin, val)  
    bridge.virtualWrite(target_virtual_pin, val)

blynk.email([to,] subject, body)    "to" can default to as set at APP   
    INCLUDE WIDGET AT APP  
blynk.notify(message)  
    INCLUDE WIDGET AT APP 
blynk.tweet(message)  untested  

Incoming digital "write" will automatically output to GPIO pins (using OnOff)  
Incoming digital "read" will automatically read GPIO pins (using OnOff) and return that status to APP,  
        but no control is available that way over pullup/pulldown resistors.  
For any more customised gpio functions, use virtual pins.   
       ie, this library has no option to custom code for GPIO pins at user script level: use virtual pins!

## Example Files:

01-simplest.js  
02-gpio-io.js  
03-media0.js  
04-media.js  
05-rlogger.js  
06-jlogger.js  
07-pir.js  
08-misc.js  
09-sensor.js  
11-accel-b.js  
11-accel.js  
12-gps-b.js  
12-gps.js  
13-pwm.js  
14-terminals.js  
15-camerashot.js  
18-bridge.js  
19-email.js  
99-ALL.js 


Brian Lavery  
brian@blavery.com  
V 0.3.5  
May 2017










