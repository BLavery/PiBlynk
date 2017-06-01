#!/usr/bin/env nodejs

// Make sure an email widget is put onto APP screen (no setup needed)

// email format = (email address,   subject,   body_of_email )

// Or, if you want to use the email address set in the App widget, omit the "to" field:
// blynk.email("Subject: Button Logger", "You just pushed the button...");


require("./mytoken"); // fetch auth tokens from sep file
var blynk = new (require("piblynk")).Blynk(token);  

PLEASE EDIT YOUR OWN EMAIL ADDRESS FOUR LINES BELOW, AND THEN DELETE THIS ADVICE LINE

blynk.on('connect', function() { 
    console.log("Blynk up. Email demo. "); 
    // as soon as permitted (ie, blynk = up) we send mail:
    blynk.email("junior@XXXXX.moc", "blynk email demo", "test 1 of blynk email\nBrian");
    console.log("Sent email to Blynk server");
    console.log(" ... and that all folks.");
});
