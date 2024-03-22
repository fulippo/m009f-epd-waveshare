import logging
from . import epdconfig

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

    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(4)
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
    
    def send_data2(self, data): #faster
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def busy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = epdconfig.digital_read(self.busy_pin)
        while(busy == 0):
            self.send_command(0x71)
            busy = epdconfig.digital_read(self.busy_pin)
        epdconfig.delay_ms(200)
        logger.debug("e-Paper busy release")
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
            
        self.reset()
        self.busy()
        
        # self.send_command(0x06)   # btst
        # self.send_data(0x17)
        # self.send_data(0x17)
        # self.send_data(0x38)      # If an exception is displayed, try using 0x38
        # self.send_data(0x17)

        self.send_command(0x4D)
        self.send_data(0x55)

        self.send_command(0xA6)
        self.send_data(0x38)

        self.send_command(0xB4)
        self.send_data(0x5D)
        
        self.send_command(0xB6)
        self.send_data(0x80)

        self.send_command(0xB7)
        self.send_data(0x00)

        self.send_command(0xF7)
        self.send_data(0x02)

        self.send_command(0x04)
        epdconfig.delay_ms(100)
        self.busy()
        logger.debug("Init complete")
    
        return 0

    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if(imwidth == self.width and imheight == self.height):
            img = img.convert('1')
        elif(imwidth == self.height and imheight == self.width):
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert('1')
        else:
            logger.warning("Wrong image dimensions: must be " + str(self.width) + "x" + str(self.height))
            # return a blank buffer
            return [0x00] * (int(self.width/8) * self.height)

        buf = bytearray(img.tobytes('raw'))
        # The bytes need to be inverted, because in the PIL world 0=black and 1=white, but
        # in the e-paper world 0=white and 1=black.
        for i in range(len(buf)):
            buf[i] ^= 0xFF
        return buf

    def display(self, imageblack, imagered):
        self.send_command(0x10)
        # The black bytes need to be inverted back from what getbuffer did
        for i in range(len(imageblack)):
            imageblack[i] ^= 0xFF
        self.send_data2(imageblack)

        self.send_command(0x13)
        self.send_data2(imagered)
        
        self.send_command(0x12)
        epdconfig.delay_ms(100)
        self.busy()
        
    def clear(self):
        buf = [0x00] * (int(self.width/8) * self.height)
        buf2 = [0xff] * (int(self.width/8) * self.height)
        self.send_command(0x10)
        self.send_data2(buf2)
            
        self.send_command(0x13)
        self.send_data2(buf)
                
        self.send_command(0x12)
        epdconfig.delay_ms(100)
        self.busy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.busy()
        
        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
### END OF FILE ###

