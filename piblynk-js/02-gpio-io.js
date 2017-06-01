#!/usr/bin/env nodejs
// 4 buttons requiring pullups
// 1 PIR GPIO input - nothing needed in this script
// 3 LEDs - nothing needed in this script
// ... and a LED "alive" icon to flash on the APP

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token);  
blynk.on('connect', function() { print("Blynk up. " + timeNow());  });


//----------------------------------------------------
// GPIO use:  OnOff used internally in blynk-rpi3 ONLY for plain GPIO outputs / inputs
//            OnOff implementation is basic, and can't even do input pullups, 
//               ... so we don't use it below in our own code
//            We use Rpio for our own regular GPIO I/O (without sudo)

var rpio = require('rpio');
rpio.init({gpiomem: true, mapping: 'gpio'});  // gpiomem mode
// all gpio numbering is BCM

//-------------------------

function timeNow() {
  var d = new Date();
  var min  = d.getMinutes();
  min = (min < 10 ? "0" : "") + min;
  var sec  = d.getSeconds();
  sec = (sec < 10 ? "0" : "") + sec;
  var hrs  = d.getHours();
  hrs = (hrs < 10 ? "0" : "") + hrs;
  return(hrs + ":" + min + ":" + sec);
};


//-----------------------------------


// input buttons with pullup: 2 different ways to do


var but1=13, but2=6, but3=26, but4=19;  // the gpio pins
var V1 = new blynk.VirtualPin(1);
var V2 = new blynk.VirtualPin(2);
var V3 = new blynk.VirtualPin(3);
var V4 = new blynk.VirtualPin(4);

function readButton(pin, VP) {  
    // 1st method: use value display at phone, which regularly requests over a VP.
    rpio.open(pin, rpio.INPUT, rpio.PULL_UP);
    VP.on('read', function() { VP.write(1-rpio.read(pin)); });
};

function sendButton(pin, VP) {  
    // 2nd method: use a LED at phone, which makes no request, just listens. (or val displ in push mode)
    // So push data from here each button up or down.
    rpio.open(pin, rpio.INPUT, rpio.PULL_UP); 
    rpio.poll(pin, function () {   VP.write(255-rpio.read(pin)*255);  });  
};

readButton(but1, V1);    // method1
sendButton(but2, V2);    // method2
sendButton(but3, V3);
sendButton(but4, V4);

//-------------------------------

// LEDs for on/off

// red led on gpio 21,   green on 20,   blue on 16
// blynk seems to write to output gpios natively,  using PIN GPIO (not virtual) addresses on APP.
// so we have nothing to code !!!

//-------------------------


//  Blinking LED widget at APP screen.

var Vled = new blynk.VirtualPin(15);
var bright = 0;  
setInterval(function(){ 
    // we put a LED widget on APP at V15.   Let's slowly blink it on phone. (not too much messaging)
    // LED widget doesn't have regular READ. We push its data from here (repeat timer)
    Vled.write(bright);  
    bright = bright+85;   // different increment -> more/less brightness levels
    if(bright > 255) bright = 0;  //wrap

  }, 1000);   // 1 per second

/*
 * At APP:
 * Value Display V1 for Button1, 1sec readrate
 * LEDs on V2 V3 V4 for buttons 2 3 4
 * LED for "alive?" indicator, V15
 * Value Display GPIO14 for PIR
 * Buttons GPIO 21 20 16 to drive the RGB leds at RPI
*/


