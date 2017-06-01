#!/usr/bin/env nodejs
// Joystick widget at APP
// Proximity sensor at APP
// Light sensor at APP
// RPI time to APP
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
// show some stuff on it
oled.yell("Hello");



// Joystick
var jstik = new blynk.VirtualPin(20);
jstik.on('write', function(param) {
  print('JoyStick:', param[0], param[1]);
});

// light
var light = new blynk.VirtualPin(25);
light.on('write', function(param) {
      oled.setCursor(65,56);
      oled.writeString('Lit: ' + param[0].toString());
});

// proximity
var prox = new blynk.VirtualPin(24);
prox.on('write', function(param) {
      oled.setCursor(5,56);
      oled.writeString('Prx: ' + param[0].toString());
});


var timeReq = new blynk.VirtualPin(10);
timeReq.on('read', function() {

  timeReq.write(timeNow());

});

/*
 * At RPI:
 * oled on i2c   128x64 0x3c
 * 
 * At APP:
 * Joystick V20
 * Proximity sensor V24
 * Light sensor V25
 * Value Display on V10, 2 sec requests
*/

