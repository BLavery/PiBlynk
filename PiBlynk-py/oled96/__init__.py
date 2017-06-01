#!/usr/bin/env python

#    USAGE:
#    from oled96 import oled
#        or
#    import oled96
#    oled = oled96.OLED(0x3c)    or 3d

from PIL import Image, ImageDraw, ImageFont
from smbus import SMBus


font1 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 12)
font2 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 19)
font3 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 36)
#font4 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 12)
font5 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 19)
#font6 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 36)

class OLED():

    def __init__(self, address=0x3C):
        try:
            self.bus = SMBus(1)     
        except:
            try:
                self.bus = SMBus(0)   
            except:
                exit(7)
        self.cmd_mode = 0x00
        self.data_mode = 0x40
        self.addr = address
        self.width = 128
        self.height = 64
        self.pages = int(self.height / 8)
        self.image = Image.new('1', (self.width, self.height))
        self.canvas = ImageDraw.Draw(self.image) # this is a "draw" object for preparing display contents
        self.jnl4=["","Jnl:","",""]


        self._command(
            const.DISPLAYOFF,
            const.SETDISPLAYCLOCKDIV, 0x80,
            const.SETMULTIPLEX,       0x3F,
            const.SETDISPLAYOFFSET,   0x00,
            const.SETSTARTLINE,
            const.CHARGEPUMP,         0x14,
            const.MEMORYMODE,         0x00,
            const.SEGREMAP,
            const.COMSCANDEC,
            const.SETCOMPINS,         0x12,
            const.SETCONTRAST,        0xCF,
            const.SETPRECHARGE,       0xF1,
            const.SETVCOMDETECT,      0x40,
            const.DISPLAYALLON_RESUME,
            const.NORMALDISPLAY,
            const.DISPLAYON)

    def _command(self, *cmd):
        assert(len(cmd) <= 31)
        self.bus.write_i2c_block_data(self.addr, self.cmd_mode, list(cmd))

    def _data(self, data):
        # In our library, only data operation used is 128x64 long, ie whole canvas.
        for i in range(0, len(data), 31):
            self.bus.write_i2c_block_data(self.addr, self.data_mode, list(data[i:i+31]))


    def display(self):
        """
        The image on the "canvas" is flushed through to the hardware display.
        Takes the 1-bit image and dumps it to the SSD1306 OLED display.
        """

        self._command(
            const.COLUMNADDR, 0x00, self.width-1,  # Column start/end address
            const.PAGEADDR,   0x00, self.pages-1)  # Page start/end address

        pix = list(self.image.getdata())
        step = self.width * 8
        buf = []
        for y in range(0, self.pages * step, step):
            i = y + self.width-1
            while i >= y:
                byte = 0
                for n in range(0, step, self.width):
                    byte |= (pix[i + n] & 0x01) << 8
                    byte >>= 1

                buf.append(byte)
                i -= 1

        self._data(buf) # push out the whole lot

    def cls(self):
        self.blank()
        self.display()
        
    def blank(self):
        self.canvas.rectangle((0, 0, self.width-1, self.height-1), outline=0, fill=0)

    def onoff(self, onoff):
        if onoff == 0:
            self._command(const.DISPLAYOFF)
        else:
            self._command(const.DISPLAYON)

    #  ABOVE are raw oled functions
    #  BELOW are some pre-formatted layouts 
    
    

    def msgBox(self,hdr="", str1="", str2="", str3=""):  # header autocentred
        oled.blank()
        self.canvas.rectangle((0, 19, oled.width-1, oled.height-1), outline=1, fill=0)
        self.canvas.text((2+(11-len(hdr))/2*124/11, 2, 0), hdr, font=font5, fill=1)
        self.canvas.text((4,23), str1, font=font1, fill=1)
        self.canvas.text((4,36), str2, font=font1, fill=1)
        self.canvas.text((4,49), str3, font=font1, fill=1)
        oled.display() 

    def yell2(self,str1="", str2=""):   # 11 char max x 2 lines
        oled.blank()
        self.canvas.text((2, 10), str1, font=font2, fill=1)
        self.canvas.text((2,40), str2, font=font2, fill=1)
        oled.display() 

    def yell(self,str1="", str2=""):  # 5 char max, 1 line
        oled.blank()
        self.canvas.text((2, 20), str1, font=font3, fill=1)
        oled.display() 

    def bar(self,str1,val,dispval=None):   # val = 0 to 100 for graph, dispval if different from val. Autocentre.
        oled.blank()
        if dispval == None:
            dispval = val
        dispval = str(int(dispval))
        #print(2+(11-len(str1))/2*124/11)
        self.canvas.text((2+(11-len(str1))/2*124/11, 2), str1, font=font5, fill=1)
        self.canvas.rectangle((0, 31, oled.width-1, 40), outline=1, fill=1)
        self.canvas.rectangle((int((val*126)/100), 32, oled.width-2, 39), outline=1, fill=0)
        self.canvas.text((2+(11-len(dispval))/2*124/11,43), dispval, font=font2, fill=1)
        oled.display() 

    def jnl(self,str1):
        oled.blank()
        self.jnl4.pop(0)
        self.jnl4.append(str1)
        self.canvas.rectangle((0, 0, oled.width-1, oled.height-1), outline=1, fill=0)
        self.canvas.text((4, 3), self.jnl4[0], font=font1, fill=1)
        self.canvas.text((4,18), self.jnl4[1], font=font1, fill=1)
        self.canvas.text((4,33), self.jnl4[2], font=font1, fill=1)
        self.canvas.text((4,48), self.jnl4[3], font=font1, fill=1)
        oled.display() 
        

class const:
    CHARGEPUMP = 0x8D
    COLUMNADDR = 0x21
    COMSCANDEC = 0xC8
    COMSCANINC = 0xC0
    DISPLAYALLON = 0xA5
    DISPLAYALLON_RESUME = 0xA4
    DISPLAYOFF = 0xAE
    DISPLAYON = 0xAF
    EXTERNALVCC = 0x1
    INVERTDISPLAY = 0xA7
    MEMORYMODE = 0x20
    NORMALDISPLAY = 0xA6
    PAGEADDR = 0x22
    SEGREMAP = 0xA0
    SETCOMPINS = 0xDA
    SETCONTRAST = 0x81
    SETDISPLAYCLOCKDIV = 0xD5
    SETDISPLAYOFFSET = 0xD3
    SETHIGHCOLUMN = 0x10
    SETLOWCOLUMN = 0x00
    SETMULTIPLEX = 0xA8
    SETPRECHARGE = 0xD9
    SETSEGMENTREMAP = 0xA1
    SETSTARTLINE = 0x40
    SETVCOMDETECT = 0xDB
    SWITCHCAPVCC = 0x2

oled = OLED()

import sys
if __name__ == '__main__':
    print (sys.argv[0], 'is an importable module:')
    exit()

