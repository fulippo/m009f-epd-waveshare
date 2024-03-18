import spidev
import RPi.GPIO as GPIO
import time

class EPD:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 5000000

        self.LCD_XSIZE = 800  # 水平大小
        self.LCD_YSIZE = 480  # 垂直大小

        self.E_Paper_BS = 9
        self.EPD_Rest = 11
        self.E_Paper_DC = 10
        self.E_Paper_CS = 3
        self.E_Paper_SCK = 5
        self.E_Paper_SDI = 7
        self.E_Paper_BUSY = 0
        self.E_Paper_DC = 6

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.EPD_Rest, GPIO.OUT)
        GPIO.setup(self.E_Paper_DC, GPIO.OUT)
        GPIO.setup(self.E_Paper_CS, GPIO.OUT)
        GPIO.setup(self.E_Paper_SCK, GPIO.OUT)
        GPIO.setup(self.E_Paper_SDI, GPIO.OUT)
        GPIO.setup(self.E_Paper_BUSY, GPIO.IN)

    def EPD_SPI_Write(self, value):
        for i in range(8):
            GPIO.output(self.E_Paper_SCK, 0)
            if value & 0x80:
                GPIO.output(self.E_Paper_SDI, 1)
            else:
                GPIO.output(self.E_Paper_SDI, 0)
            time.sleep(0.000001)
            GPIO.output(self.E_Paper_SCK, 1)
            time.sleep(0.000001)
            value = (value << 1)
        GPIO.output(self.E_Paper_SCK, 0)

    def EPD_SPI_Read(self):
        rdata = 0
        for i in range(8):
            GPIO.output(self.E_Paper_SCK, 0)
            time.sleep(0.000002)
            GPIO.output(self.E_Paper_SCK, 1)
            time.sleep(0.000002)
            rdata <<= 1
            if GPIO.input(self.E_Paper_SDI):
                rdata |= 0x01
            time.sleep(0.000002)
        GPIO.output(self.E_Paper_SCK, 0)
        return rdata

    def EPD_WriteCMD(self, command):
        GPIO.output(self.E_Paper_CS, 0)
        GPIO.output(self.E_Paper_DC, 0)
        time.sleep(0.00001)
        self.EPD_SPI_Write(command)
        GPIO.output(self.E_Paper_CS, 1)

    def EPD_WriteDATA(self, data):
        GPIO.output(self.E_Paper_CS, 0)
        GPIO.output(self.E_Paper_DC, 1)
        time.sleep(0.00001)
        self.EPD_SPI_Write(data)
        GPIO.output(self.E_Paper_CS, 1)

    def EPD_Check_Busy(self):
        while True:
            if not GPIO.input(self.E_Paper_BUSY):
                break

    def EPD_initial(self):
        GPIO.output(self.EPD_Rest, 0)
        time.sleep(0.05)
        GPIO.output(self.EPD_Rest, 1)
        time.sleep(0.05)
        self.EPD_Check_Busy()

        self.EPD_WriteCMD(0x4D)
        self.EPD_WriteDATA(0x55)

        self.EPD_WriteCMD(0xA6)
        self.EPD_WriteDATA(0x38)

        self.EPD_WriteCMD(0xB4)
        self.EPD_WriteDATA(0x5D)

        self.EPD_WriteCMD(0xB6)
        self.EPD_WriteDATA(0x80)

        self.EPD_WriteCMD(0xB7)
        self.EPD_WriteDATA(0x00)

        self.EPD_WriteCMD(0xF7)
        self.EPD_WriteDATA(0x02)

        self.EPD_WriteCMD(0x04)
        time.sleep(0.1)
        self.EPD_Check_Busy()

    def EPD_refresh(self):
        self.EPD_WriteCMD(0x12)
        time.sleep(0.3)
        self.EPD_Check_Busy()

    def EPD_sleep(self):
        self.EPD_WriteCMD(0X02)
        time.sleep(0.1)
        self.EPD_Check_Busy()
        self.EPD_WriteCMD(0X07)
        self.EPD_WriteDATA(0xA5)

    def EPD_display_BMP(self, WK_data, R_data):
        x_size = self.LCD_XSIZE // 8 if self.LCD_XSIZE % 8 else self.LCD_XSIZE // 8 + 1
        self.EPD_WriteCMD(0x10)
        for _ in range(self.LCD_YSIZE):
            for _ in range(x_size):
                self.EPD_WriteDATA(WK_data)
                WK_data += 1

        self.EPD_WriteCMD(0x13)
        for _ in range(self.LCD_YSIZE):
            for _ in range(x_size):
                self.EPD_WriteDATA(R_data)
                R_data += 1

        self.EPD_refresh()
        self.EPD_sleep()


