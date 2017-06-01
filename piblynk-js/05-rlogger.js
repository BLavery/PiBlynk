#!/usr/bin/env nodejs


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


//-----------------------------------

myIP = require('my-local-ip')();
myPID = process.pid;
myHostname = require("os").hostname();




ctr=0;
rlogger = new blynk.VirtualPin(18);

// initial message out:
setTimeout(function(){
	rlogger.write("\nip:"+myIP+"  pid:"+myPID+"  "+myHostname+"\n");
	}, 2000);  // slight delay: allowing for blynk to get connected to server

 
// dummy regular text to logger  
setInterval(function(){ 
  rlogger.write(timeNow()+ " "+ctr++ + "\n"); 
   print(timeNow());

  },5000);

/*
 * At APP:
 * make terminal widget on that V18, fill whole phone screen, 
 * turn off its input box
 * now it is a live-time remote log display screen rpi->app  with rlogger.write()
 * but server WONT indefinitely buffer messages if APP is offline.
*/



