#!/usr/bin/env nodejs

// accelerometer.  BETTER METHOD.  Use of software "widget"
// buffered data, pitch&roll calculations 

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");
var blynk = new Blynk.Blynk(token);  // ssl default
//var blynk = new Blynk.Blynk(token, options = {  connector : new Blynk.TcpClient() });  // straight tcp

var blynk_up = false;   // we keep up/down status to avoid blind tx to Vxx pins when down.
blynk.on('connect', function() {  
    print("Blynk up. " ); 
    blynk_up = true; 
    });



//-------------------------


accel = new blynk.WidgetAccel(17);


setInterval(function(){ 
   print(accel.pitch(), accel.roll(), accel.age());
}, 2000);  

// at APP:
// accelerometer widget, to VPin 17
