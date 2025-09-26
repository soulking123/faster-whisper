import board
import neopixel
import time

# --- Configuration ---
PIXEL_COUNT = 16  # The number of LEDs in your ring
LED_PIN = board.D18 # GPIO 18 (Data line)
BRIGHTNESS = 0.3    # Set brightness (0.0 to 1.0)
ORDER = neopixel.GRB # WS2812 generally uses GRB order

# Initialize the strip
pixels = neopixel.NeoPixel(LED_PIN, PIXEL_COUNT, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)

# --- Example Function ---
def color_wipe(color, wait):
    for i in range(PIXEL_COUNT):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

# --- Main Program ---
try:
    print("Starting LED test...")
    # Fill the ring with a solid red color
    color_wipe((255, 0, 0), 0.05) # Red
    time.sleep(2)

    # Turn off the LEDs
    pixels.fill((0, 0, 0))
    pixels.show()

except KeyboardInterrupt:
    # Turn off the LEDs on exit
    pixels.fill((0, 0, 0))
    pixels.show()
