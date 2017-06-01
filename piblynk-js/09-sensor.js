#!/usr/bin/env nodejs
// Proximity sensor at APP
// Light sensor at APP
// oled

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token);  
blynk.on('connect', function() { print("Blynk up. " + timeNow());  });


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



// init oled

var Oled = require('oled-rpi');
var opts = {height: 64};
var oled = new Oled(opts);
oled.yell("Sensors");



// light & proximity - create buffered reception of sensor data stream.
var light = new blynk.WidgetSensor(25);
var prox = new blynk.WidgetSensor(24);

// periodically fetch latest values & do something with them
function oled_out_cb() {
    oled.writeJnl("L:"+String(light.value) + " P:"+String(prox.value)+" "+timeNow());
    // console.log("L:"+String(light.value) + " P:"+String(prox.value)+" "+timeNow());
}

setInterval(oled_out_cb,5000);



/*
 * At RPI:   
 * oled on i2c   128x64 0x3c
 * 
 * At APP:
 * Proximity sensor V24
 * Light sensor V25
*/

