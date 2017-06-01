
import os

from PiBlynk import Blynk
from mytoken import *
blynk = Blynk(token)


#------------------------------------------
import time
def timeNow():
    return time.asctime()[11:19]

#------------------------------------

# terminal from APP into python interpreter
_last_cmd = ""
def pyterminal_h(value, pin, st):
        global _last_cmd
        cmd = value[0]
        if cmd == ".":
            cmd = _last_cmd
            blynk.virtual_write(pin, "> "+cmd+"\n")
        else:
            _last_cmd = cmd
        try:
            out = eval(cmd)
            if out != None:
                outstr = "= "+repr(out)
        except:
            try:
                exec(cmd)
                outstr = "= (OK)"
            except Exception as e:
                outstr = repr(e)
        blynk.virtual_write(pin, outstr+"\n")
        

blynk.add_virtual_pin(14, None, pyterminal_h)

#--------------------------------
# Terminal from APP into OS shell

def osterminal_h(value, pin, st):
        try:
            outstr = os.popen(value[0]).read()
        except Exception as e:
            outstr = repr(e)
        blynk.virtual_write(pin, outstr)

blynk.add_virtual_pin(13, None, osterminal_h)
# These "terminals" esp the OS one could be dangerous vulnerability. 
# Be sure you really, really want to keep this in regular installation !!!!
#--------------------------------

def cnct_cb():
    print ("Connected: "+ timeNow())
blynk.on_connect(cnct_cb)



blynk.run()

# AT APP:

# terminal widget Vpin 13 for python interactive terminal 
#     Note You cannot create new variables in RPI's python,
#     But you can interrogate blynk variables/functions from user or blynk script 
#     (eg gps.age() or blynk._token )
# terminal Vpin 14 for OS (shell) interactive terminal
#     Note shell terminal has no memory between calls. 
#     So a "cd" to change directory, immediately lapses again.

