# PiBlynk
Javascript and Python libraries for using Blynk APP on Raspberry Pi
Two working libraries designed to easily connect with the Blynk smartphone APP.

The libraries are designed specifically for Raspberry Pi, although the python one should adapt well. The overall design target is for:
stability in connection
full suite of interfacing functions
similarity of functions in the two versions, as far as the languages allow 

Both are forked code, “standing on the shoulders of others.”

# Features (both versions) include:
Automatic connecting to Blynk server, and maintaining that connection.
Full suite of functions for interfacing to GPIO and virtual pins of the Blynk protocol.
Widget object for LCD
Widget for GPS (with distance and direction), 
Widget for accelerometer (with pitch and roll)
Send email, tweet, smartphone notification.
Change phone widget properties (colour, label)
Widget for a “bridge”, ie gpio or virtual commands to another hardware device.
Compatible with PiCamera
Extensive example files.


# Specific to javascript version:
Uses OnOff gpio module to allow simplistic GPIO in and out without specific coding.
Compatible also with rpio and pigpio modules as more competent GPIO libraries.
Connects to Blynk server in plain TCP or in SSL.

The javascript version requires nodejs greater than either 0.10.x as distributed on Raspbian, or the 0.12.x as found on xxxxxx.  I upgraded my nodejs using the recommended xxxxxxx to 6.x.  Unfortunately I find that all the later versions of nodejs (past 0.12.x) seem to run only on my Raspberry Pi 3 (armv7), but not on my new Pi zero-W (armv6). On the RPi3, the javascript Blynk code works great. The javascript version is inherently single-threaded.


# Specific to python version:
By default, “hardware agnostic”. Operates on any linux, and probably on Windows (unchecked)
No default GPIO library. Operates comfortably with gpiozero module.
Python (2) or python 3.
TCP connection, but no SSL.
User Tasks, ie interval timer, threaded/concurrent
One-shot Timer functions, threaded/concurrent
Reentrancy protection for threaded “write” calls.
Simple “Ticker” periodic function (not threaded)
Generic buffering widget for any sensor pushing data from APP (eg lightmeter)

The python version runs fine on any version of RPi. It uses threading for user code.

# Attributions:

The PiBlynk-py library was inspired by, and leveraged from, the work of the WIPY project.
   https://github.com/wipy/wipy/blob/master/lib/blynk/BlynkLib.py
and thence from
   https://github.com/youngsoul/BlynkLib

The piblynk-js library was derived from:
    https://github.com/vshymanskyy/blynk-library-js
    MIT licence
