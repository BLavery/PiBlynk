#!/usr/bin/env nodejs

// "Toy Telnet"
// Interactive terminals at phone for nodejs/javascript interpreter, ans OS shell

var print = console.log;   // create an alias to look like python print() !!!
var exec = require('child_process').exec;  // for shell commands


require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");
var blynk = new Blynk.Blynk(token);  // ssl default
//var blynk = new Blynk.Blynk(token, options = {  connector : new Blynk.TcpClient() });  // straight tcp

var blynk_up = false;   // we keep up/down status to avoid blind tx to Vxx pins when down.
blynk.on('connect', function() {  
    print("Blynk up. " ); 
    blynk_up = true; 
    });




//-----------------------

// Pre-make a few handy Vxx ("virtual pin") variables for blynk:
for (v=10; v<=20; v++) 
    eval("var V" + v + " = new blynk.VirtualPin(" + v + ");");  // -> V0 to V??
    


//------------------------------------

// APP terminal to execute BASH commands at RPi


V13.on('write', function(param) {
    
   try { 
       exec(param[0],
       function (error, stdout, stderr) {
          V13.write(stdout);
          V13.write(stderr);
       });
   }
   catch(err) {
       V13.write(err);
   }
});


//-------------------------------------

// APP terminal to execute Javascript commands at RPi nodejs interpreter

V14.on('write', function(param) {
    try {
        print(param[0]);
        v = eval(param[0]);
        if (typeof(v) === 'undefined') v=".";
        V14.write(v + "\n");
   }
   catch(err) {
       V14.write(err + "\n");
   }
});

// AT APP:

// terminal widget Vpin 13 for javascript interactive terminal 
// terminal Vpin 14 for OS (shell) interactive terminal
//     Note shell terminal has no memory between calls. 
//     So a "cd" to change directory, immediately lapses again.
