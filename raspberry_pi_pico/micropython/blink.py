# Micropython Blink on board LED

# Libraries
import machine
import utime

# Definition
# LED_PIN 
LED_PIN = machine.Pin(25, machine.Pin.OUT)
# Delay in seconds
DELAY = 1

# Main Loop to Toggle the LED
while True:
    # Print Message Indicate LED is turning on
    print("LED is turning ON")
    # Turn On the LED
    LED_PIN.on()
    # Wait for the specified duration
    utime.sleep(DELAY)
    # Print Message Indicate LED is turning off
    print("LED is turning OFF")
    # Turn Off the LED
    LED_PIN.off()
    # Wait for specified duration
    utime.sleep(DELAY)
