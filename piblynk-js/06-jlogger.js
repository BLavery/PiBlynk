#!/usr/bin/env nodejs
// Typed entries at APP get displayed JNL style at OLED on RPI

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
oled.yell("Jlogger");


var jlogr = new blynk.VirtualPin(19);
jlogr.on('write', function(param) {
    oled.writeJnl(param[0]);
});


/*
 * At RPI:
 * oled on i2c   128x64 0x3c
 * 
 * At APP:
 * Terminal widget on V19
*/


