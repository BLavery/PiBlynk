#!/usr/bin/env nodejs


var print = console.log;   // create an alias to look like python print() !!!
require("./mytoken"); // fetch auth token from sep file
var Blynk = require("piblynk");  // Blynk "class"

// blynk object.  comment out one of following tcp / ssl:
var blynk = new Blynk.Blynk(token); // default to ssl
//var blynk = new Blynk.Blynk(token,options={connector: new Blynk.TcpClient()});  // straight tcp

blynk.on('connect', function() { 
    print("Blynk up " + timeNow());
    blynk.setProperty(22, "color", "#23C48E");   // force led colour at APP
});
blynk.on('disconnect', function() { print("Blynk down " + timeNow());  });
//////blynk.on("network", function(updown) { print("Net", updown); });

myIP = require('my-local-ip')();
myPID = process.pid;
myHostname = require("os").hostname();
var exec = require('child_process').exec;   // to execute shell command
var camera = new (require('campi'))();   //  https://github.com/vesteraas/campi
var fs = require('fs');


//-------------------------

// GPIO use:  OnOff library used internally in blynk-rpi3 ONLY for plain GPIO outputs / inputs
//            OnOff implementation is basic, and can't even do input pullups, 
//               ... so we don't use it below in our own code
//            We use Rpio for our own regular GPIO I/O (without sudo)
//  So what about more GPIO features eg PWM? We will need SUDO:
//            Rpio can be run in sudo mode ("sudo nodejs xxxx.js"),
//               ... and more functions become available (pwm/i2c/spi)
//            PiGpio ALWAYS needs sudo but can do even fancier things 
//               ... like PWM, servo and ultrasonic (pulse and timing features)
//  On any one gpio pin, use only one gpio regime.

// Conclusion: we can take our pick of most convenient gpio library to use (OnOff, pigpio, rpio)
//   for each/any GPIO pin.  Except certain functionality will also need SUDO.


// Below, we choose to set up rpio library by default
// and if SUDO is in effect, we add the pigpio library too

sudo = (parseInt(process.env.SUDO_UID)>=1000);   // test if sudo


var rpio = require('rpio');
if (sudo) {
    // init the more competent functions if sudo. Load pigpio and upgrade rpio
    var piGpio = require('pigpio').Gpio;   
    // Pigpio always needs sudo.
    // refer https://www.npmjs.com/package/pigpio
    rpio.init({gpiomem: false, mapping: 'gpio'}); 
    // Rpio optionally uses sudo, but we use a slightly different memory-mapping mode 
    // refer https://www.npmjs.com/package/rpio
} 
else {
    rpio.init({gpiomem: true, mapping: 'gpio'});  
    // gpiomem mode for non-sudo, some functions n/a, like pwm
}
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

// Pre-make a few handy Vxx ("virtual pin") variables for blynk:
for (v=0; v<=30; v++) 
    eval("var V" + v + " = new blynk.VirtualPin(" + v + ");");  // -> V0 to V??
    
//-----------------------------------



// init oled

var Oled = require('oled-rpi');
var opts = {height: 64};
var oled = new Oled(opts);
// show some stuff on it
oled.setCursor(5,30);
oled.writeString("the Lot", 3);

// Fortunately, the oled-rpi library is benign, in that, if OLED hardware is not present,
// no errors are raised, either now or later at any oled.xx() call

//----------------------------

// input buttons with pullup: 2 different ways to do


var but1=13, but2=6, but3=26, but4=19;  // the gpio pins
// we use V1 V2 V3 V4

function readButton(pin, VP) {  
    // 1st method: use value display at phone, which regularly requests over a VP.
    rpio.open(pin, rpio.INPUT, rpio.PULL_UP);
    VP.on('read', function() { VP.write(1-rpio.read(pin)); });
};

function sendButton(pin, VP) {  
    // 2nd method: use a LED at phone, which makes no request, just listens. (or val displ in push mode)
    // So push data from here each button up or down.
    rpio.open(pin, rpio.INPUT, rpio.PULL_UP); 
    rpio.poll(pin, function () { VP.write(255-rpio.read(pin)*255); });  
};

readButton(but1, V1);    // method1
sendButton(but2, V2);    // method2
sendButton(but3, V3);    // method2
sendButton(but4, V4);    // method2

//-------------------------------

// LEDs for on/off

// red led on gpio 21,   green on 20,   blue on 16
// blynk seems to write to output gpios natively,  using PIN GPIO (not virtual) addresses on APP.
// so we have nothing to code !!!

//-------------------------

// 1 LED for PWM control  - we use pigpio module which needs sudo operation
var pwmvalu=0;
var Vpwm = V8;
var Vgauge = V9;

if(! sudo) {
    print("PWM? - will merely emulate LED PWM (because not sudo!)"); 
}
if(sudo) {
    var blueled = new piGpio(16, {mode: piGpio.OUTPUT});   // the pigpio object at pin 16, the blue led
    blueled.pwmWrite(0);
}
// NOTE: if we don't have sudo status, we still preserve the "pwmvalu" for echoing back to APP on V9
Vpwm.on('write', function(param) {
      pwmvalu = param[0];   // preserve a copy for later   0 - 255
      if (sudo) blueled.pwmWrite(pwmvalu);
      print(pwmvalu);
});
// If pwm is set to 0 (off), then native LED/OUT control as per prev para can work.
// For pwm>0, pwm has precedence.


// a readback to APP of the above pwm led value (even if pwm is not running because of no sudo)

Vgauge.on('read', function() {
  Vgauge.write(pwmvalu);
});

//----------------------------



//  Blinking LED widget at APP screen.
// ... and using same timer, sending time to LCD on V33

var lcd = new blynk.WidgetLCD(33);  // takes Vxx number. (Creates its own VP)

var Vled = V15;
var ledctrl = 0; 
var colours = ["#23C48E","#04C0F8","#ED9D00","#D3435C","#5F7CD8","#FFFFFF","#44FF44","#FF4444","#4444FF"];

setInterval(function(){ 
    // we put a LED widget on APP at V15.   Let's slowly blink it on phone. (not too much messaging)
    // LED widget doesn't have regular READ. We push its data from here (repeat timer)
    Vled.write((ledctrl & 1)*255);  
    Vled.setProperty("color", colours[ledctrl%9]);   // and change its colour
    ledctrl = (ledctrl+1)%17;  

    
    // LCD widget:
	lcd.clear();
    lcd.print(0,0,timeNow()); // line 0
    lcd.print(0,1,"from "+myHostname);  // line 1


  }, 1500);   

//-----------------------

// jlogger

var jlogr = V19;
jnl = ["", "", "", "", "Jnl"];
jlogr.on('write', function(param) {
	jnl = jnl.slice(1); // drop top line
	jnl[4] = param[0];  // add new 5th line
	oled.clearDisplay(false); // delay the screen write
	for (i=0; i<5; i++) {
		oled.setCursor(5, 5+i*13);
		oled.writeString(jnl[i],1,false,false);  // delay the screen write
	}
	oled.update();  // finally, update screen
});

//------------------


// Joystick
var jstik = V20;
jstik.on('write', function(param) {
  print('JoyStick:', param[0], param[1]);
});

// light
var light = V25;
light.on('write', function(param) {
      oled.setCursor(65,56);
      oled.writeString('Lit: ' + param[0].toString());
});

// proximity
var prox = V24;
prox.on('write', function(param) {
      oled.setCursor(5,56);
      oled.writeString('Prx: ' + param[0].toString());
});


var timeReq = V10;
timeReq.on('read', function() {

  timeReq.write(timeNow());

});

//------------------------

// rlogger



ctr=0;
rlogger = V18;

// initial message out:
setTimeout(function(){
	rlogger.write("\nip:"+myIP+"  pid:"+myPID+"  "+myHostname+"\n");
	}, 2000);  // slight delay: allowing for blynk to get connected to server

 
// dummy regular text to logger  
setInterval(function(){ 
  rlogger.write(timeNow()+ " "+ctr++ + "\n"); 
  },10000);

//----------------

// Media buttons for Clementine player


//  Blinking LED widget at APP screen.

blynk.setProperty(22, "color", "#D3435C");
var Vled2 = V22;
var bright2 = 0;  
setInterval(function(){ 
  // we put a LED widget on phone APP.   Let's  blink it on phone. 
  bright2 = 255-bright2;
  if (stopped)   bright2=0;   // if player stopped, no led flash at APP
  Vled2.write(bright2);  
}, 500);   // 2/sec ie rather fast

var vol = V23;
vol.on('write', function(param) { 
    exec("clementine -v "+ param[0]);
});


stopped = false;
var mediaButtons = V21;
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

//---------------------


// PIR sensor.  needs no pullup. 
// (altho, a pulldown might avoid floating if pir not fitted!)
// sends to notify widget at APP. no requirement for a VPin
var pir=14;

rpio.open(pir, rpio.INPUT); // plain gpo input w/o pullup
rpio.poll(pir, function () {   // detect rises & falls
	if(rpio.read(pir) == 1)   // only on rise
	    blynk.notify("PIR alert " + timeNow());  
});  

//----------------------

// GPS from APP
// this is a hand-coded version.  See 12-gps-b.js for simpler way using library widgetGPS

Vgps = V11;
Vdist = V12;//-----------------------------------

var lat1 = 0, lon1=0, distance = 0;

Vgps.on('write', function(param) {
  t = String(new Date()).slice(16,21);  
  // print(t, ' GPS Lat:', param[0], " Long:", param[1], param[2], param[3]);

  oled.clearDisplay();
  oled.setCursor(5,1);
  oled.writeString('Lat: ' + param[0].toString());
  oled.setCursor(5,18);
  oled.writeString("Lon: " + param[1].toString());
  oled.setCursor(5,33);

  if (lat1 === 0) {
      lat1 = param[0];   // first gps reading sets lat1, lon1 the starting place
      lon1 = param[1];
      V24.write(1, lat1, lon1+0.1, "value");
  }
  else {
      distance = 1000*getDistanceFromLatLonInKm(lat1, lon1, param[0], param[1]);  // in metres
      V24.write(2, param[0]+0.1, param[1], "value2");
  }
  oled.writeString(timeNow() + " " + Math.round(distance));
});

function getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in km
  return d;
}

// http://stackoverflow.com/questions/18883601/function-to-calculate-distance-between-two-coordinates-shows-wrong
function deg2rad(deg) {
  return deg * (Math.PI/180)
}


// APP reads GPS dist away from start


Vdist.on('read', function() {
  Vdist.write("GPS Dist: " + Math.round(distance) + " m");
});



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
jvparam="";
V14.on('write', function(param) {
    try {
        par=String(param[0]);
        if (par === ".") {   // dot = repeat last command
			par = jvparam;
			V14.write("> " + par + "\n");
		}
		else 
			jvparam = par;
        v = eval(par);
        if (typeof(v) === 'undefined') v=".";
        V14.write(v + "\n");
   }
   catch(err) {
       V14.write(err + "\n");
   }
});


//---------------------------------

// 3 values x/y/z from phone/tablet accelerometer
var ctr2 = 0;
V17.on('write', function(param) {
  //print('Accel:', param[0], param[1], param[2]);
  if (ctr2 % 50 === 0) {  // try not overload oled function. display 1 in xx readings
      oled.clearDisplay(false);   // delay display
      oled.setCursor(5,1);
      oled.writeString("X: "+ Math.round(100*param[0])/100,2, false, false);  // delay display
      oled.setCursor(5,20);
      oled.writeString("Y: "+ Math.round(100*param[1])/100,2, false, false);
      oled.setCursor(5,38);
      oled.writeString("Z: "+ Math.round(100*param[2])/100,2);   // now display
  }
  ctr2++;
});
// A neater version using accelerometer widget is in example 11-accel-b.js

//----------------------------


// RPi Camera support.   
// Needs (1) Camera set on in RPi configurator, (2) camera plugged in
// Do a camera test to check it exists:
var cam_exists=true;

try { 
    exec("raspistill -set -n",    // a status read from camera
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
picName = V27;
camButton = V26;
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



// Incoming V-Pin to control the green ACT led on RPI3
// https://github.com/raspberrypi/linux/issues/1332
//
// Following is RPI3 (only) special function to use a APP button on V30
// to make ACT LED on pcb flash when button ON

var ACTLED_timer = null;
var ACTLED_state = false;
V30.on("write", function(param) {
	clearInterval(ACTLED_timer);
	if (param[0] >0) 
		ACTLED_timer = setInterval(ACTLED_toggle, 300);
	else 
		exec('sudo sh -c "echo mmc0 > /sys/class/leds/led0/trigger"');
});

function ACTLED_toggle() {
	ACTLED_state = ! ACTLED_state;
	if (ACTLED_state)
		exec('sudo sh -c "echo none > /sys/class/leds/led0/trigger"');
	else
		exec('sudo sh -c "echo default-on > /sys/class/leds/led0/trigger" ');
};
// RPI2 and RPIzero are different from RPI3.  
// See https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
// But anyway, newer nodejs versions run only on ARMv7 (rpi3)
	

