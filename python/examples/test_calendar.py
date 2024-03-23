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
from gcsa.google_calendar import GoogleCalendar


logging.basicConfig(level=logging.DEBUG)



def drawRow(pil_image, text, font, row_number = 1):
  row_height = 98
  row_width = 478
  x0 = 0
  x1 = row_width
  y0 = (row_number-1) * row_height
  y1 = row_number * row_height
  pil_image.rectangle([x0, y0, x1, y1], outline = 0, width=1)
  pil_image.text((10, y0), text, font = font, fill = 0)


try:
    epd = EPD()
    logging.info("init and Clear")
    epd.init()
    epd.clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    now = datetime.datetime.now()
    day = now.strftime('%A %d')

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    black_image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    red_image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_black_image = ImageDraw.Draw(black_image)
    
    draw_black_image.text((10, 0), day, font = font48, fill = 0)
    draw_black_image.rectangle([0, 0, 478, 98], outline = 0, width=1)
    calendar = GoogleCalendar('filippo.pisano@gmail.com')
    home_calendar = calendar.get_calendar('8i0ce1apg9n092h2rq91ao07n0@group.calendar.google.com')
    drawRow(draw_black_image, day, font48)
    row_number=2
    for event in home_calendar:
        drawRow(draw_black_image, event.summary, font18, row_number=row_number)
        row_number+=1

    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    time.sleep(120)


    logging.info("Clear...")
    epd.init()
    epd.clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd.module_exit(cleanup=True)
    exit()
