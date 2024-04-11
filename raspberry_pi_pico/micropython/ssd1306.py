'''
Micropython SSD1306 oled driver,
i2c and spi interfaces
'''

# Libraries
from micropython import const
import framebuf

# SSD1306 Definitions
SSD1306_CONTRAST           = const(0x81)
SSD1306_ENTIRE_ON          = const(0xA4)
SSD1306_NORM_INV           = const(0xA6)
SSD1306_SET_DISP           = const(0xAE)
SSD1306_MEM_ADDR           = const(0x20)
SSD1306_COL_ADDR           = const(0x21)
SSD1306_PAGE_ADDR          = const(0x22)
SSD1306_DISP_START_LINE    = const(0x40)
SSD1306_SEG_REMAP          = const(0xA0)
SSD1306_MUX_RATIO          = const(0xA8)
SSD1306_COM_OUT_DIR        = const(0xC0)
SSD1306_DISP_OFFSET        = const(0xD3)
SSD1306_COM_PIN_CFG        = const(0xDA)
SSD1306_DISP_CLK_DIV       = const(0xD5)
SSD1306_PRECHARGE          = const(0xD9)
SSD1306_VCOM_DESEL         = const(0xDB)
SSD1306_CHARGE_PUMP        = const(0x8D)

# Subclassing framebuffer provides support for
# graphic primitives
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width         = width
        self.height        = height
        self.external_vcc  = external_vcc
        self.pages         = self.height // 8
        self.buffer        = byteArray(self.pages *self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()
    
    def init_display(self)
        for cmd in ( # OFF
                     SSD1306_SET_DISP | 0x00,
                     # Address Setting
                     SET_MEM_ADDR,
                     # Horizontal
                     0x00,
                     # Resolution and Layout
                     SSD1306_DISP_START_LINE | 0X00,
                     # Column addr 127 mapped to SEG0
                     SSD1306_SEG_REMAP       | 0x01,
                     SSD1306_MUX_RATIO,
                     self_height - 1,
                     # Scan from COM[N] to COM0
                     SSD1306_COM_OUT_DIR | 0x08,
                     SSD1306_DISP_OFFSET,
                     0x00,
                     SSD1306_COM_PIN_CFG,
                     0x02 if self.width > 2 * self.height else 0x12,
                     # Timing and Driving Scheme
                     SSD1306_DISP_CLK_DIV,
                     0x80,
                     SSD1306_PRECHARGE,
                     0x22 if self.external_vcc else 0xF1,
                     SSD1306_VCOM_DESEL,
                     # 0x83 * Vcc
                     0x30,
                     # Display
                     SSD1306_CONTRAST,
                     # Maximum
                     0xFF,
                     # Output Follows RAM Contents
                     SSD1306_ENTIRE_ON,
                     # Not Inverted
                     SSD1306_NORM_INV,
                     # Charge Pump
                     SSD1306_CHARGE_PUMP,
                     0x10 if self.external_vcc else 0x14,
                     SSD1306_SET_DISP | 0x01,
                   ):
            #ON
            self.write_cmd(cmd)
            self.fill(0)
            self.show()
    
    def power_off(self):
        self.write_cmd(SSD1306_SET_DISP | 0x00)
    
    def power_on(self):
        self.write_cmd(SSD1306_SET_DIS | 0x01)
    
    def contrast(self, contrast):
        self.write_cmd(SSD1306_CONTRAST)
        self.write_cmd(contrast)
    
    def invert(self, invert):
        self.write_cmd(SSD1306_NORM_INV | (invert & 1))
    
    def show (self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # Displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SSD1306_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SSD1306_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)gg

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc = False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        # Co=0, D/C#=1
        self.write_list = [b"\x40", None]
        super().__init__(width, height, external_vcc)
    
    def write_cmd(self, cmd):
        # Co=1, D/C#=0
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)
    
    def write_data(self, buf):
        self.write_list[1] = buf;
        self.i2c_writevto(self.addr, self.write_list)

class SSD1306_SPI(SSD1306)
    def __init__(self, width, height, spi, dc, res, cs, external_vcc = False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value = 0)
        res.init(res.OUT, value = 0)
        cs.init(cs.OUT, value = 1)
        self.spi = spi
        self.dc  = dc
        self.res = res
        self.cs  = cs
        import time
        
        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate = self.rate, polarity = 0, phase = 0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)
    
    def write_data(self, buf):
        self.spi.init(baudrate = self.rate, polarity = 0, phase = 0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
