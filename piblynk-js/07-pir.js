#!/usr/bin/env nodejs

// 1 PIR GPIO input - nothing needed in this script


var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token);  
blynk.on('connect', function() { print("Blynk up. " + timeNow());  });



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

// PIR sensor.  needs no pullup. 
// (altho, a pulldown might avoid floating if pir not fitted!)
// sends to notify widget at APP. no requirement for a VPin
var pir=14;

rpio.open(pir, rpio.INPUT); // plain gpo input w/o pullup
rpio.poll(pir, function () {   // detect rises & falls
	if(rpio.read(pir) == 1)  { // only on rise
	    blynk.notify("PIR alert " + timeNow()); // to app on phone
	    print("PIR alert", timeNow());
	    //blynk.email("bflavery@gmail.com", "PIR", "PIR alert at " + timeNow());
	    // email not working?
	} 
});  

// AT APP:
// simply a "notification" icon on screen
