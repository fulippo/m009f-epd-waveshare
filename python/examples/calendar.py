#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'images')
drivers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'drivers')

if os.path.exists(drivers_dir):
    sys.path.append(drivers_dir)

import logging
from mf_17502_m009f import EPD
import time
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.DEBUG)



try:
    epd = EPD()
    logging.info("init and Clear")
    epd.init()
    epd.clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    now = datetime.datetime.now()
    day = now.strftime("%A")

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_Himage = ImageDraw.Draw(Himage)
    
    draw_Himage.text((10, 0), day, font = font24, fill = 0)
    draw_Himage.text((10, 20), '7.5inch e-Paper', font = font24, fill = 0)
    draw_Himage.line((140, 75, 190, 75), fill = 0)
    draw_Himage.arc((140, 50, 190, 100), 0, 360, fill = 0)
    draw_Himage.rectangle((80, 50, 130, 100), fill = 0)
    draw_Himage.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage), [])
    time.sleep(2)


    logging.info("Clear...")
    epd.init()
    epd.clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    EPD.module_exit(cleanup=True)
    exit()
