#!/usr/bin/env nodejs

// Accelerometer, RPi plain data listening on vPin

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


accel = new blynk.VirtualPin(17);

// 3 values x/y/z from phone/tablet accelerometer

accel.on('write', function(param) {
  print('Accel:', param[0], param[1], param[2], "\033[1A");

});

// at APP:
// accelerometer widget, to VPin 17
