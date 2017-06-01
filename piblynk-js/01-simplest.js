#!/usr/bin/env nodejs

// 3 LEDs - nothing needed in this script - plain gpio output
// 1 PIR - again, nothing to code - plain gpio input (no pullups needed)

require("./mytoken"); // fetch auth token from sep file
var blynk = new (require("piblynk")).Blynk(token);  

// at APP:
// 3 buttons to GPIOs 21, 20, 16
// 1 display value from GPIO14, polled 2 sec intervals

