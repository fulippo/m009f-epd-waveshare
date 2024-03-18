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
        epdconfig.delay_ms(10)
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

    def refresh(self):
        self.send_command(0x12) # DISPLAY_REFRESH
        epdconfig.delay_ms(300)
        self.ReadBusyH()
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        self.ReadBusyH()
        epdconfig.delay_ms(30)

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
        self.ReadBusyH()
        return 0

    def getbuffer(self, image):
        # Create a pallette with the 4 colors supported by the panel
        pal_image = Image.new("P", (1,1))
        pal_image.putpalette( (0,0,0,  255,255,255,  255,0,0) + (0,0,0)*253)

        # Check if we need to rotate the image
        imwidth, imheight = image.size
        #logger.info(f"Image size")
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
        buf = [0x00] * int(self.width * self.height / 3)
        idx = 0
        for i in range(0, len(buf_4color), 3):
            buf[idx] = (buf_4color[i] << 5) + (buf_4color[i+1] << 2) + (buf_4color[i+2] >> 1)
            #buf[idx] = (buf_4color[i] << 6) + (buf_4color[i+1] << 4) + (buf_4color[i+2] << 2) + buf_4color[i+3]
            idx += 1
        return buf

    def display(self, image):
        Width = self.width // 4
        Height = self.height

        self.send_command(0x04)
        self.ReadBusyH()
        #logger.debug(f"image is {image}")

        self.send_command(0x10)
        for j in range(0, Height):
            for i in range(0, Width):
                    self.send_data(image[i + j * Width])
        self.TurnOnDisplay()
        
    def Clear(self, color=0x55):
        Width = self.width // 4
        Height = self.height

        self.send_command(0x04)
        self.ReadBusyH()

        self.send_command(0x10)
        for j in range(0, Height):
            for i in range(0, Width):
                self.send_data(color)

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        epdconfig.delay_ms(300)
        self.ReadBusyH()
        epdconfig.module_exit()
### END OF FILE ###

