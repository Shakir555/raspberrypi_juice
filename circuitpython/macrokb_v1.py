# Libraries
import time
import digitalio
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# Set up Keyboard and Mouse
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

# Set up Buttons
# Copy Button
copy_btn = digitalio.DigitalInOut(board.GP6)
copy_btn.direction = digitalio.Direction.INPUT
copy_btn.pull = digitalio.Pull.DOWN
# Paste Button
paste_btn = digitalio.DigitalInOut(board.GP2)
paste_btn.direction = digitalio.Direction.INPUT
paste_btn.pull = digitalio.Pull.DOWN

# Select Word Function
def select_word():
    mouse.click(Mouse.LEFT_BUTTON)
    time.sleep(0.1)
    mouse.click(Mouse.LEFT_BUTTON)
    time.sleep(0.1)

# Copy Function
def copy():
    print("Copy Button Pressed, CTRL+C Initiated" )
    select_word()
    keyboard.press(Keycode.CONTROL, Keycode.C)
    time.sleep(0.1)
    keyboard.release(Keycode.CONTROL, Keycode.C)
    print("Copy Completed")

# Paste Function
def paste():
    print("Paste Button Pressed, CTRL+V Initiated")
    keyboard.press(Keycode.CONTROL, Keycode.V)
    time.sleep(0.1)
    keyboard.release(Keycode.CONTROL, Keycode. V)
    print("Paste Completed")

# Handle Button Function
def handle_button(button, action):
    if button.value:
        action()
        time.sleep(0.3)
        
print("Macro Keyboard Started. Press CTRL+C to exit")
try:
    while True:
        handle_button(copy_btn, copy)
        handle_button(paste_btn, paste)
        time.sleep(0.01)

# Keyboard Interrupt Handler
except KeyboardInterrupt:
    print("Stopped bu user")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Cleaning Up...")
