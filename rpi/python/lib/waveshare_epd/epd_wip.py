# *****************************************************************************
# * | File        :	  epd7in3g.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1
# * | Date        :   2022-07-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from . import epdconfig

import PIL
from PIL import Image
import io

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

logger = logging.getLogger(__name__)

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.BLACK  = 0x000000   #   00  BGR
        self.WHITE  = 0xffffff   #   01
        self.RED    = 0x0000ff   #   11
        
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)         # module reset
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)
        
    def ReadBusyH(self):
        logger.debug("e-Paper busy H")
        while(epdconfig.digital_read(self.busy_pin) == 0):      # 0: idle, 1: busy
            epdconfig.delay_ms(5)
        logger.debug("e-Paper busy H release")

    def ReadBusyL(self):
        logger.debug("e-Paper busy L")
        while(epdconfig.digital_read(self.busy_pin) == 1):      # 0: busy, 1: idle
            epdconfig.delay_ms(5)
        logger.debug("e-Paper busy L release")

    def TurnOnDisplay(self):
        self.send_command(0x12) # DISPLAY_REFRESH
        self.send_data(0x01)
        self.ReadBusyH()

        self.send_command(0x02) # POWER_OFF
        self.send_data(0X00)
        self.ReadBusyH()
        
    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 0):      # 0: idle, 1: busy
            epdconfig.delay_ms(100)    
        logger.debug("e-Paper busy release")
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x01) # POWER_SETTING
        self.send_data2([0x37, 0x00])
        
        self.send_command(0x00) # PANEL_SETTING
        self.send_data2([0xCF, 0x08])
        
        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data2([0xc7, 0xcc, 0x28])
        
        self.send_command(0x04) # POWER_ON
        self.ReadBusy()
        
        self.send_command(0x30) # PLL_CONTROL
        self.send_data(0x3c)
        
        self.send_command(0x41) # TEMPERATURE_CALIBRATION
        self.send_data(0x00)
        
        self.send_command(0x50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x77)
        
        self.send_command(0x60) # TCON_SETTING
        self.send_data(0x22)
        
        self.send_command(0x61) # TCON_RESOLUTION
        self.send_data(EPD_WIDTH >> 8)     #source 640
        self.send_data(EPD_WIDTH & 0xff)
        self.send_data(EPD_HEIGHT >> 8)     #gate 384
        self.send_data(EPD_HEIGHT & 0xff)
        
        self.send_command(0x82) # VCM_DC_SETTING
        self.send_data(0x1E) # decide by LUT file
        
        self.send_command(0xe5) # FLASH MODE
        self.send_data(0x03)
        
        # EPD hardware init end
        return 0

    def getbuffer(self, image):
        # Create a pallette with the 4 colors supported by the panel
        pal_image = Image.new("P", (1,1))
        pal_image.putpalette( (0,0,0,  255,255,255,  255,255,0,   255,0,0) + (0,0,0)*252)

        # Check if we need to rotate the image
        imwidth, imheight = image.size
        if(imwidth == self.width and imheight == self.height):
            image_temp = image
        elif(imwidth == self.height and imheight == self.width):
            image_temp = image.rotate(90, expand=True)
        else:
            logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, self.width, self.height))

        # Convert the soruce image to the 4 colors, dithering if needed
        image_4color = image_temp.convert("RGB").quantize(palette=pal_image)
        buf_4color = bytearray(image_4color.tobytes('raw'))

        # into a single byte to transfer to the panel
        buf = [0x00] * int(self.width * self.height // 3)
        idx = 0
        for i in range(0, len(buf_4color), 3):
            buf[idx] = (buf_4color[i] << 5) + (buf_4color[i+1] << 2) + (buf_4color[i+2] >> 1)
            idx += 1

        
    def display(self, image):
        self.send_command(0x10)
        self.send_data2(image)
        self.send_command(0x12)
        epdconfig.delay_ms(100)
        self.ReadBusy()
        
    def Clear(self):
        buf = [0x33] * int(self.width * self.height / 2)
        self.send_command(0x10)
        self.send_data2(buf)
        self.send_command(0x12)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.send_data(0x00)

        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)
### END OF FILE ###

