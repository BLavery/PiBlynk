#!/usr/bin/env nodejs

// Button on phone to take camera snapshot at RPi.

var print = console.log;   // create an alias to look like python print() !!!
var exec = require('child_process').exec;
var camera = new (require('campi'))();   //  https://github.com/vesteraas/campi
var fs = require('fs');


require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");
var blynk = new Blynk.Blynk(token);  // ssl default
//var blynk = new Blynk.Blynk(token, options = {  connector : new Blynk.TcpClient() });  // straight tcp

blynk.on('connect', function() {  
    print("Blynk up. " + timeNow()); 
    });


//-------------------------

function timeNow() {
  var d = new Date();
  var min  = d.getMinutes();
  min = (min < 10 ? "0" : "") + min;
  var sec  = d.getSeconds();
  sec = (sec < 10 ? "0" : "") + sec;
  return(d.getHours() + "." + min + "." + sec);
};

// RPi Camera support.   
// Needs (1) Camera set on in RPi configurator, (2) camera plugged in
// Do a camera test to check it exists:
var cam_exists=true;

try { 
    exec("raspistill -set",    // a status read from camera
    function (error, stdout, stderr) {
       if(stderr.includes("not detected")){ 
			print("No camera fitted");
			cam_exists = false;
		}
       if(stderr.includes("not enabled")){ 
			print("RPi config not enabling camera.");
			cam_exists = false;
		}
    });
}
catch(err) { throw err; }
cam_busy = true;
setTimeout(function(){ cam_busy = false;}, 8000);
// That "test" we did times out on some internal process after a few secs.
// If we try camerashot before that, will crash. Let's wait (arbitrary) time.
 
//-----------------------
picName = new blynk.VirtualPin(27);
camButton = new blynk.VirtualPin(26);
//----------------------------

imageDir = "images";


cam_options= {  
            width: 640,
            height: 480,
            nopreview: true,
            timeout: 1,
            hflip: true,
            vflip: true
        };
        
 
function CamShot(imageName) {  
	if (! cam_exists) {
		return "No Cam";
	}
    if (cam_busy) {
		return "Busy !";   // reject another request too soon. Wait until first is done (abt 1 sec?)
    }
    cam_busy = true;  
    if(!fs.existsSync(imageDir)) {
        fs.mkdirSync(imageDir, 0744);   // create images directory if not there
    } ;
    var iName = imageDir+"/"+imageName+".jpg";  
    
    // all now in order to take our shot:
    // but defer the camera operation until an async moment later

    setTimeout(function(){
        // The callback takes abt 50 (first) or 15 (repeat) mSec elapsed to execute.
        camera.getImageAsFile(cam_options, iName, function (err) {  
            if (err) {
                //throw err;
                print(err);
            }
            cam_busy = false;
        });
    }, 50); 
	return imageName;
};


// rpi camera still-shot, from APP button on V26, and pic id returned on V27

camButton.on("write", function(param) {
    if (param[0] == 1)  {  // button press
		fname = "RPi-"+timeNow();  //proposed image name
		fname = CamShot(fname);  // name may be changed on error
		print(fname);
		picName.write(fname);
	}});

//----------------------------------

// At APP: 
// Button to Vpin 26. Momentary, not staydown action
// Value Display Vpin 27 in listen-only mode (no timer) for confirmed shot filename or error message

