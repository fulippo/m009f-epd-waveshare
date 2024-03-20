#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd_wip22
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd_wip2 Demo")

    epd = epd_wip2.EPD()   
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
        epd.display(epd.getbuffer(Himage))
        time.sleep(3)
        logging.info("Clear...")
        epd.Clear()
    
    
    

    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd_wip2.epdconfig.module_exit(cleanup=True)
    exit()
