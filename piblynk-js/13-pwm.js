#!/usr/bin/env nodejs

//Using BLUE LED.
//Slider on APP to control brightness.
//Gauge on APP, polling for current PWM brightness value to confirm

// MUST BE RUN AS SUDO !!!

var print = console.log;   // create an alias to look like python print() !!!
var exec = require('child_process').exec;  // for shell commands
var camera = new (require('campi'))();   //  https://github.com/vesteraas/campi
var fs = require('fs');


require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");
var blynk = new Blynk.Blynk(token);  // ssl default
//var blynk = new Blynk.Blynk(token, options = {  connector : new Blynk.TcpClient() });  // straight tcp

var blynk_up = false;   // we keep up/down status to avoid blind tx to Vxx pins when down.
blynk.on('connect', function() {  
    print("Blynk up. " ); 
    blynk_up = true; 
    });


//----------------------------------------------------

sudo = (parseInt(process.env.SUDO_UID)>=1000);   // test if sudo
print("SUDO =",sudo);

// GPIO use:  OnOff used internally in blynk-rpi3 ONLY for plain GPIO outputs / inputs
//            OnOff implementation is basic, and can't even do input pullups, 
//               ... so we don't use it below in our own code
//            We use Rpio for our own regular GPIO I/O (without sudo)
//            Rpio can also be run in sudo mode ("sudo nodejs xxxx.js"),
//               ... and more functions become available (pwm/i2c/spi)
//            PiGpio always needs sudo but can do even fancier things like servo and ultrasonic
//            On any one gpio pin, use only one gpio regime.

// below uses pigpio (instead of rpio) in sudo mode

var piGpio = require('pigpio').Gpio; 
if(! sudo) {
    print("NEED SUDO.  For now, APP will merely emulate LED PWM"); 
}
// all gpio numbering is BCM


//-----------------------

// Pre-make a few handy Vxx ("virtual pin") variables for blynk:
for (v=0; v<=10; v++) 
    eval("var V" + v + " = new blynk.VirtualPin(" + v + ");");  // -> V0 to V??
    
//-----------------------------------


// 1 LED for PWM control  - we use pigpio module which needs sudo operation
var pwmvalu=0;
var Vpwm = V8;
var Vgauge = V9;

if(sudo) {
    var blueled = new piGpio(16, {mode: piGpio.OUTPUT});   // the pigpio object at pin 16, the blue led
    blueled.pwmWrite(0);
}
// NOTE: if we don't have sudo status, we still preserve the "pwmvalu" for echoing back to APP on V9
Vpwm.on('write', function(param) {
      pwmvalu = param[0];   // preserve a copy for later   0 - 255
      if (sudo) blueled.pwmWrite(pwmvalu);
      print(pwmvalu);
});



//--------------------------------

// a readback to APP of the above pwm led value (even if pwm is not running because of no sudo)

Vgauge.on('read', function() {
  Vgauge.write(pwmvalu);
});

//----------------------------

// AT APP:
// slider (H or V) to Vpin 8. Set to write at end of each slide action. Scaled 0-100 (think "percent")
// gauge polling Vpin 9.  Scaled 0-1.   (pigpio scales pwm 0.0 - 1.0)
