#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd_wip
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

def getbuffer(image):
    # Create a pallette with the 4 colors supported by the panel
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  255,0,0) + (0,0,0)*253)

    # Check if we need to rotate the image
    imwidth, imheight = image.size
    #logger.info(f"Image size")
    if(imwidth == 800 and imheight == 480):
        image_temp = image
    elif(imwidth == 480 and imheight == 800):
        image_temp = image.rotate(90, expand=True)
    else:
        logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, self.width, self.height))

    # Convert the soruce image to the 4 colors, dithering if needed
    image_4color = image_temp.convert("RGB").quantize(palette=pal_image)
    
    buf_4color = bytearray(image_4color.tobytes('raw'))

    # into a single byte to transfer to the panel
    buf = [0x00] * int(self.width * self.height / 3)
    idx = 0
    for i in range(0, len(buf_4color), 3):
        buf[idx] = (buf_4color[i] << 5) + (buf_4color[i+1] << 2) + (buf_4color[i+2] >> 1)
        #buf[idx] = (buf_4color[i] << 6) + (buf_4color[i+1] << 4) + (buf_4color[i+2] << 2) + buf_4color[i+3]
        idx += 1
    return buf

    epd = epd_wip.EPD()
    epd.EPD_initial()
def main():
    try:
        logging.info("epd_wip Demo")


        logging.info("init and Clear")
        epd.init()
        epd.clear()
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
        
        while True:
            # Drawing on the image
            logging.info("1.Drawing on the image...")
            Himage = Image.new('RGB', (epd.width, epd.height), epd.WHITE)  # 255: clear the frame
            draw = ImageDraw.Draw(Himage)
            # draw.text((5, 0), 'hello world', font = font18, fill = epd.RED)


            # draw.line((5, 170, 80, 245), fill = epd.RED)
            
            # draw.rectangle((5, 170, 80, 245), outline = epd.BLACK)
            
            # draw.arc((5, 250, 80, 325), 0, 360, fill = epd.BLACK)
            # draw.chord((90, 250, 165, 325), 0, 360, fill = epd.RED)
            #epd.display(getbuffer(Himage))
            epd.EPD_display_BMP(getbuffer(Himage), getbuffer(Himage))
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd_wip.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
    time.sleep(3)
    logging.info("Clear...")
        

