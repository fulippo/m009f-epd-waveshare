import RPi.GPIO as GPIO
import time
from PIL import Image
import numpy as np
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')


LCD_XSIZE = 800
LCD_YSIZE = 480

E_Paper_BS = 9
EPD_Rest = 11
E_Paper_DC = 10
E_Paper_CS = 3
E_Paper_SCK = 5
E_Paper_SDI = 7
E_Paper_BUSY = 0

def delay_us(microseconds):
    time.sleep(microseconds / 1000000.0)

def EPD_SPI_Write(value):
    E_Paper_SCK = 0
    for i in range(8):
        E_Paper_SCK = 0
        if value & 0x80:
            E_Paper_SDI = 1
        else:
            E_Paper_SDI = 0
        delay_us(1)
        E_Paper_SCK = 1
        delay_us(1)
        value = (value << 1)
    E_Paper_SCK = 0

def EPD_SPI_Read():
    rdata = 0
    for i in range(8):
        E_Paper_SCK = 0
        delay_us(2)
        E_Paper_SCK = 1
        delay_us(2)
        rdata <<= 1
        if E_Paper_SDI:
            rdata |= 0x01
        delay_us(2)
    E_Paper_SCK = 0
    return rdata

def EPD_WriteCMD(command):
    GPIO.output(E_Paper_CS, GPIO.LOW)
    GPIO.output(E_Paper_DC, GPIO.LOW)  # command write
    delay_us(10)
    EPD_SPI_Write(command)
    GPIO.output(E_Paper_CS, GPIO.HIGH)

def EPD_WriteDATA(data):
    GPIO.output(E_Paper_CS, GPIO.LOW)
    GPIO.output(E_Paper_DC, GPIO.HIGH)  # data write
    delay_us(10)
    EPD_SPI_Write(data)
    GPIO.output(E_Paper_CS, GPIO.HIGH)

def EPD_Check_Busy():
    while True:
        if GPIO.input(E_Paper_BUSY) == 0:
            break

def EPD_initial():
    GPIO.output(EPD_Rest, GPIO.LOW)
    delay_ms(50)
    GPIO.output(EPD_Rest, GPIO.HIGH)
    delay_ms(50)

    EPD_Check_Busy()  # ic enter normal

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

    EPD_WriteCMD(0x04)  # POWER ON
    delay_ms(100)
    EPD_Check_Busy()

def EPD_refresh():
    EPD_WriteCMD(0x12)  # DISPLAY REFRESH
    delay_ms(300)
    EPD_Check_Busy()

def EPD_sleep():
    EPD_WriteCMD(0X02)  # power off
    delay_ms(100)
    EPD_Check_Busy()
    EPD_WriteCMD(0X07)  # deep sleep
    EPD_WriteDATA(0xA5)

def EPD_display_BMP(WK_data, R_data):
    x_size = LCD_XSIZE // 8 if LCD_XSIZE % 8 else LCD_XSIZE // 8 + 1
    # Write Data
    EPD_WriteCMD(0x10)  # Transfer old data
    for _ in range(LCD_YSIZE):
        for _ in range(x_size):
            EPD_WriteDATA(WK_data)
            WK_data += 1

    # write red and white data
    EPD_WriteCMD(0x13)
    for _ in range(LCD_YSIZE):
        for _ in range(x_size):
            EPD_WriteDATA(R_data)
            R_data += 1

    EPD_refresh()
    EPD_sleep()

def load_image(file_path):
    image = Image.open(file_path)
    image = image.convert("L")  # Convert to grayscale
    image = image.resize((800, 480))
    return np.array(image)

def convert_image(image):
    # Convert image to 1-bit (black and white) format
    threshold = 128
    bw_image = (image > threshold).astype(np.uint8) * 255
    return bw_image

def display_image(image_file):
    

    # Load image from file
    image = load_image(image_file)

    # Convert image to 1-bit format
    bw_image = convert_image(image)

    # Display image on e-paper display
    EPD_initial()
    EPD_display_BMP(bw_image.flatten(), bw_image.flatten())

if __name__ == "__main__":
    image_file = os.path.join(picdir, '7in3f1.bmp')  # Change this to your image file path
    display_image(image_file)
