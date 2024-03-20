import RPi.GPIO as GPIO
import time
import os
import sys
from PIL import Image, ImageDraw, ImageFont

from logging import Logger as logger
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

EPD_WIDTH = 800
EPD_HEIGHT = 480

BLACK  = 0x000000   #   0000  BGR
WHITE  = 0xffffff   #   0001
RED    = 0x0000ff   #   0100


# Define GPIO pin numbers
E_Paper_BS_PIN = 31
EPD_Rest_PIN = 23
E_Paper_DC_PIN = 19
E_Paper_CS_PIN = 5
E_Paper_SCK_PIN = 29
E_Paper_SDI_PIN = 21
E_Paper_BUSY_PIN = 11

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(E_Paper_BS_PIN, GPIO.OUT)
GPIO.setup(EPD_Rest_PIN, GPIO.OUT)
GPIO.setup(E_Paper_DC_PIN, GPIO.OUT)
GPIO.setup(E_Paper_CS_PIN, GPIO.OUT)
GPIO.setup(E_Paper_SCK_PIN, GPIO.OUT)
GPIO.setup(E_Paper_SDI_PIN, GPIO.OUT)
GPIO.setup(E_Paper_BUSY_PIN, GPIO.IN)

# Define delay functions
def delay_us(delay):
    time.sleep(delay / 1000000.0)

def delay_ms(delay):
    time.sleep(delay / 1000.0)

# Define functions equivalent to the C functions
def EPD_SPI_Write(value):
    for i in range(8):
        GPIO.output(E_Paper_SCK_PIN, GPIO.LOW)
        if value & 0x80:
            GPIO.output(E_Paper_SDI_PIN, GPIO.HIGH)
        else:
            GPIO.output(E_Paper_SDI_PIN, GPIO.LOW)
        delay_us(1)
        GPIO.output(E_Paper_SCK_PIN, GPIO.HIGH)
        delay_us(1)
        value = (value << 1)
    GPIO.output(E_Paper_SCK_PIN, GPIO.LOW)

def EPD_WriteCMD(command):
    GPIO.output(E_Paper_CS_PIN, GPIO.LOW)
    GPIO.output(E_Paper_DC_PIN, GPIO.LOW)
    delay_us(10)
    EPD_SPI_Write(command)
    GPIO.output(E_Paper_CS_PIN, GPIO.HIGH)

def EPD_WriteDATA(data):
    GPIO.output(E_Paper_CS_PIN, GPIO.LOW)
    GPIO.output(E_Paper_DC_PIN, GPIO.HIGH)
    delay_us(10)
    EPD_SPI_Write(data)
    GPIO.output(E_Paper_CS_PIN, GPIO.HIGH)

def EPD_Check_Busy():
    while True:
        if GPIO.input(E_Paper_BUSY_PIN) == GPIO.LOW:
            break

def EPD_initial():
    GPIO.output(EPD_Rest_PIN, GPIO.LOW)
    delay_ms(50)
    GPIO.output(EPD_Rest_PIN, GPIO.HIGH)
    delay_ms(50)
    EPD_Check_Busy()
    EPD_WriteCMD(0x4D)
    EPD_WriteDATA(0x55)
    EPD_WriteCMD(0xA6)
    EPD_WriteDATA(0x38)
    EPD_WriteCMD(0xB4)
    EPD_WriteDATA(0x5D)
    EPD_WriteCMD(0xB6)
    EPD_WriteDATA(0x80)
    EPD_WriteCMD(0xB7)
    EPD_WriteDATA(0x00)
    EPD_WriteCMD(0xF7)
    EPD_WriteDATA(0x02)
    EPD_WriteCMD(0x04)
    delay_ms(100)
    EPD_Check_Busy()

def EPD_refresh():
    EPD_WriteCMD(0x12)
    delay_ms(300)
    EPD_Check_Busy()

def EPD_sleep():
    EPD_WriteCMD(0x02)
    delay_ms(100)
    EPD_Check_Busy()
    EPD_WriteCMD(0x07)
    EPD_WriteDATA(0xA5)

def EPD_display_BMP(WK_data):
    x_size = EPD_WIDTH // 8 if EPD_WIDTH % 8 == 0 else EPD_WIDTH // 8 + 1
    EPD_WriteCMD(0x10)
    for _ in range(EPD_HEIGHT):
        for _ in range(x_size):
            EPD_WriteDATA(WK_data)
            WK_data += 1

    # EPD_WriteCMD(0x13)
    # for _ in range(EPD_HEIGHT):
    #     for _ in range(x_size):
    #         EPD_WriteDATA(R_data)
    #         R_data += 1

    EPD_refresh()
    EPD_sleep()


def getbuffer(image):
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  255,0,0) + (0,0,0)*253)

    # Check if we need to rotate the image
    imwidth, imheight = image.size
    if(imwidth == EPD_WIDTH and imheight == EPD_HEIGHT):
        image_temp = image
    elif(imwidth == EPD_HEIGHT and imheight == EPD_WIDTH):
        image_temp = image.rotate(90, expand=True)
    else:
        logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, 800, 600))

    # Convert the soruce image to the 7 colors, dithering if needed
    image_3color = image_temp.convert("RGB").quantize(palette=pal_image)
    image_3color = bytearray(image_3color.tobytes('raw'))
    return image_3color

def getimage():
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    Himage = Image.new('RGB', (EPD_WIDTH, EPD_HEIGHT), WHITE)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((5, 0), 'hello world', font = font18, fill = RED)


    # draw.line((5, 170, 80, 245), fill = epd.RED)
    
    # draw.rectangle((5, 170, 80, 245), outline = epd.BLACK)
    
    # draw.arc((5, 250, 80, 325), 0, 360, fill = epd.BLACK)
    # draw.chord((90, 250, 165, 325), 0, 360, fill = epd.RED)
    return getbuffer(Himage)
    

if __name__ == "__main__":
    EPD_initial()
    EPD_display_BMP(getimage())

    