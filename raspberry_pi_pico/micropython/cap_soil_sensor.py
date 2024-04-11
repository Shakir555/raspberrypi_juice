'''
Micropython Capacitive Soil Sensor
'''

# Libraries
from machine import ADC, Pin, I2C
from ssd1306 import SSD1306_I2C
import utime

# Variables
# Soil Moisture PIN reference
soil = ADC(Pin(26))

# Calibration Values
min_moisture = 19200
max_moisture = 49300

# Delay Between Readings
readDelay = 0.5

# OLED Display Width
WIDTH = 128
# OLED Display Height
HEIGHT = 64

# Init I2C using pins GP0 & GP1
i2c = I2C(0, scl = Pin(1), sda = Pin(0), freq = 200000)
# Display device Address 
print("I2C Address : "+hex(i2c.scan()[0]).upper())
# Display I2c Config
print("I2c Configuration: "+str(i2c))

# Init OLED Display
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

while True:
    oled.fill(0)
    # Read Moisture Value and convert
    # to percentage into the calibration range
    moisture = (max_moisture - soil.read_u16()) * 100 / (max_moisture - min_moisture)
    # Print Values
    print("moisture: " + "%.2f" % moisture +"% (adc: "+ str(soil.read_u16()) + ")")
    oled.text("Soil Moisture ", 10 ,15)
    oled.text(str ("%.2f" % moisture) + " %", 35, 35)
    oled.show()
    # Set a delay between readings 
    utime.sleep(readDelay)
