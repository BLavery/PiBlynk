#!/usr/bin/env nodejs

// GPS from APP.
// Alternative version, using gps-widget .
// No oled.

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");
//var blynk = new Blynk.Blynk(token);  // ssl default
var blynk = new Blynk.Blynk(token, options = {  connector : new Blynk.TcpClient() });  // straight tcp

var blynk_up = false;   // we keep up/down status to avoid blind tx to Vxx pins when down.
blynk.on('connect', function() {  
    print("Blynk up. " + timeNow()); 
    blynk_up = true; 
    });


//----------------------------------------------------


//-------------------------

function timeNow() {
  var d = new Date();
  var min  = d.getMinutes();
  min = (min < 10 ? "0" : "") + min;
  var sec  = d.getSeconds();
  sec = (sec < 10 ? "0" : "") + sec;
  return(d.getHours() + ":" + min + ":" + sec);
};

//-----------------------



gps = new blynk.WidgetGPS(11);


setInterval(function(){ 
   console.log(gps.latitude, gps.longtitude, "dist/dir:", gps.distance(), gps.direction(), "age",gps.age());
}, 10000);  

// GPS from APP

Vdist = new blynk.VirtualPin(12);//-----------------------------------

//----------------------------

// APP reads GPS dist away from start


Vdist.on('read', function() {
  Vdist.write("GPS Dist: " + Math.round(gps.distance()) + " m "  + Math.round(gps.direction()) + " deg");
});


