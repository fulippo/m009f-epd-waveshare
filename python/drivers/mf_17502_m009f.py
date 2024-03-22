import logging
import gpiozero
import spidev
import time

logger = logging.getLogger(__name__)

class EPD:
    
    # Pin definition for Raspberry Pi
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18
    SCK_PIN  = 23

    # Display resolution
    EPD_WIDTH       = 800
    EPD_HEIGHT      = 480
        
    def __init__(self):
        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN    = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN     = gpiozero.LED(self.DC_PIN)
        # self.GPIO_CS_PIN     = gpiozero.LED(self.CS_PIN)
        self.GPIO_PWR_PIN    = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN   = gpiozero.Button(self.BUSY_PIN, pull_up = False)

        self.reset_pin = self.RST_PIN
        self.dc_pin = self.DC_PIN
        self.busy_pin = self.BUSY_PIN
        self.cs_pin = self.CS_PIN
        self.width = self.EPD_WIDTH
        self.height = self.EPD_HEIGHT

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            if value:
                self.GPIO_RST_PIN.on()
            else:
                self.GPIO_RST_PIN.off()
        elif pin == self.DC_PIN:
            if value:
                self.GPIO_DC_PIN.on()
            else:
                self.GPIO_DC_PIN.off()
        # elif pin == self.CS_PIN:
        #     if value:
        #         self.GPIO_CS_PIN.on()
        #     else:
        #         self.GPIO_CS_PIN.off()
        elif pin == self.PWR_PIN:
            if value:
                self.GPIO_PWR_PIN.on()
            else:
                self.GPIO_PWR_PIN.off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        elif pin == self.RST_PIN:
            return self.RST_PIN.value
        elif pin == self.DC_PIN:
            return self.DC_PIN.value
        # elif pin == self.CS_PIN:
        #     return self.CS_PIN.value
        elif pin == self.PWR_PIN:
            return self.PWR_PIN.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def module_init(self):
        self.GPIO_PWR_PIN.on()

        # SPI device, bus = 0, device = 0
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        
        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_PWR_PIN.off()
        logger.debug("close 5V, Module enters 0 power consumption ...")
        
        if cleanup:
            self.GPIO_RST_PIN.close()
            self.GPIO_DC_PIN.close()
            # self.GPIO_CS_PIN.close()
            self.GPIO_PWR_PIN.close()
            self.GPIO_BUSY_PIN.close()

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(4)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
    
    def send_data2(self, data): #faster
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte2(data)
        self.digital_write(self.cs_pin, 1)

    def busy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = self.digital_read(self.busy_pin)
        while(busy == 0):
            self.send_command(0x71)
            busy = self.digital_read(self.busy_pin)
        self.delay_ms(200)
        logger.debug("e-Paper busy release")
        
    def init(self):
        if (self.module_init() != 0):
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
        self.delay_ms(100)
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
        self.delay_ms(100)
        self.busy()
        
    def clear(self):
        buf = [0x00] * (int(self.width/8) * self.height)
        buf2 = [0xff] * (int(self.width/8) * self.height)
        self.send_command(0x10)
        self.send_data2(buf2)
            
        self.send_command(0x13)
        self.send_data2(buf)
                
        self.send_command(0x12)
        self.delay_ms(100)
        self.busy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.busy()
        
        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
        self.delay_ms(2000)
        self.module_exit()
### END OF FILE ###

