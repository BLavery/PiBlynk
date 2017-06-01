#!/usr/bin/env nodejs

// GPS from APP
// Displays to OLED
// The hand-coded use simply of Vpin data.
// App polls RPi for results of "distance since start" and displays at phone
// Also an example of using plain TCK connection, not secured SSL connection

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


// init oled

var oled = require('oled-rpi');
var opts = {height: 64};
var oled = new oled(opts);

// show some stuff on it
oled.setCursor(15,30);
oled.writeString("Hello", 3);


//------

// GPS from APP
Vgps = new blynk.VirtualPin(11);
Vdist = new blynk.VirtualPin(12);

var lat1 = 0, lon1=0, distance = 0;

Vgps.on('write', function(param) {
  t = String(new Date()).slice(16,21);  
  // print(t, ' GPS Lat:', param[0], " Long:", param[1], param[2], param[3]);

  oled.clearDisplay();
  oled.setCursor(5,1);
  oled.writeString('Lat: ' + param[0].toString());
  oled.setCursor(5,30);
  oled.writeString("Lon: " + param[1].toString());

  if (lat1 === 0) {
      lat1 = param[0];   // first gps reading sets lat1, lon1 the starting place
      lon1 = param[1];
      V24.write(1, lat1, lon1+0.1, "value");
  }
  else {
      distance = 1000*getDistanceFromLatLonInKm(lat1, lon1, param[0], param[1]);  // in metres
      V24.write(2, param[0]+0.1, param[1], "value2");
  }
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

//----------------------------

// APP reads GPS dist away from start


Vdist.on('read', function() {
  Vdist.write("GPS Dist: " + Math.round(distance) + " m");
});

//At APP:
// GPS widget, to Vpin 11
// Value Display Vpin 12, polling 2 sec

