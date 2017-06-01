#!/usr/bin/env nodejs

// Demo of music player buttons on APP

var print = console.log;   // create an alias to look like python print() !!!

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token);  
blynk.on('connect', function() { print("Blynk up. ");  });

//-------------------------


var mediaButtons = new blynk.VirtualPin(21);
mediaButtons.on('write', function(param) { 
    print(param[0]);
});

/*
 * At APP:
 * Media buttons widget on V21
*/
