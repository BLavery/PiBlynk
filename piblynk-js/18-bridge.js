#!/usr/bin/env nodejs

// BRIDGE demo.   Needs two devices.
// This script is for running on an EXTRA RPI device, with its own AUTH TOKEN NUMBER (important)
// Edit your file mytoken.js with a second line like the first, but nominating a "token2"

// The first RPi should have a green LED on its GPIO 20, as usual.
// This second RPi will write to the other one's led, flashing it.

require("./mytoken"); // fetch two auth tokens from sep file
var blynk = new (require("piblynk")).Blynk(token2);  // <<<< NOTE - we are device 2


blynk.on('connect', function() { 
    console.log("Blynk up. Bridge demo. "); 
    bridge.setAuthToken(token);     // <<<<<<<< NOTE
    // as soon as permitted (blynk = up) we register other RPI's project token for the bridge
    
});
var bridge = new blynk.WidgetBridge(50);  // Create a bridge channel to server. We use our vpin 50

var greenled_state = 0;
var greenled_gpio = 20; // (on that other RPi)

setInterval(function(){ 
    // our bridge widget can do DIGITAL WRITE (or virtual, too)  to the other device
    bridge.digitalWrite(greenled_gpio, greenled_state);  
    greenled_state = 1-greenled_state; // toggle 0 / 1
    console.log("Sending flash to other machine green led");

  }, 3000);   // 1 per 3 seconds

// At APP:
// place a BRIDGE widget on phone screen (permits bridging functions)

// At other RPI device #1, run say 02-gpio.js or 01-simple (any script that can output to gpio/led gpio)
// At this  RPI device #2, run this bridge script.
// 
