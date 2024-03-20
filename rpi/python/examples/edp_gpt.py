import RPi.GPIO as GPIO
import time
from PIL import Image
import numpy as np
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from edp_gpt import EPD_initial
from edp_gpt import EPD_display_BMP

E_Paper_BS = 9
EPD_Rest = 11
E_Paper_DC = 10
E_Paper_CS = 3
E_Paper_SCK = 5
E_Paper_SDI = 7
E_Paper_BUSY = 0

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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(EPD_Rest, GPIO.OUT)
    GPIO.setup(E_Paper_DC, GPIO.OUT)
    GPIO.setup(E_Paper_CS, GPIO.OUT)
    GPIO.setup(E_Paper_SCK, GPIO.OUT)
    GPIO.setup(E_Paper_SDI, GPIO.OUT)
    GPIO.setup(E_Paper_BS, GPIO.OUT)
    GPIO.setup(E_Paper_BUSY, GPIO.IN)
    image_file = os.path.join(picdir, '7in3f1.bmp')  # Change this to your image file path
    display_image(image_file)
