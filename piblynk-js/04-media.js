#!/usr/bin/env nodejs

// APP = Media player remote
// RPI is running Clementine music player

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token2);  
blynk.on('connect', function() { print("Blynk up. ");  });

//-------------------------


var exec = require('child_process').exec;   // to call shell command



//  Blinking LED widget at APP screen.
var Vled = new blynk.VirtualPin(22);
var bright = 0;  
setInterval(function(){ 
  // we put a LED widget on phone APP at V15.   Let's  blink it on phone. 
  bright = 255-bright;
  if (stopped)   bright=0;   // if player stopped, no led flash at APP
  Vled.write(bright);  
}, 500);   // 5/sec ie rather fast

var vol = new blynk.VirtualPin(23);
vol.on('write', function(param) { 
    exec("clementine -v "+ param[0]);
});


stopped = false;
var mediaButtons = new blynk.VirtualPin(21);
mediaButtons.on('write', function(param) { 
    var p = param[0];
    if (p=="play") {
        exec("clementine -p");
        stopped = false;
    }
    if (p=="stop") {
        exec("clementine -s");
        stopped = true;
    }
    if (p=="next")
        exec("clementine -f");
    if (p=="prev")
        exec("clementine -r");
    exec("clementine -y");

});

/*
 * At APP:
 * Media buttons widget on V21
 * LED widget on V22
 * Slider on V23, scaled 0 to 100
 * 
 * RPI needs "clementine" music player installed and running, with a playlist
*/
