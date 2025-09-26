import RPi.GPIO as GPIO # Import the library
import time             # Import the time module

# Pin Setup:
# Use BCM (Broadcom SOC channel) numbering for the pins
# BCM numbers correspond to the GPIO channel number, not the physical pin number
PIN1 = 23
PIN2 = 24
PIN3 = 25 
GPIO.setmode(GPIO.BCM) 
GPIO.setup(PIN1, GPIO.OUT) # Set the pin as an OUTPUT
GPIO.setup(PIN2, GPIO.OUT)
GPIO.setup(PIN3, GPIO.OUT)
try:
    # Loop 5 times
    for _ in range(5):
        GPIO.output(PIN1, GPIO.HIGH) # Turn the LED ON (HIGH voltage)
        GPIO.output(PIN2, GPIO.HIGH)
        GPIO.output(PIN3, GPIO.HIGH)
        time.sleep(1)                  # Wait for 1 second
        GPIO.output(PIN1, GPIO.LOW)  # Turn the LED OFF (LOW voltage)
        GPIO.output(PIN2, GPIO.LOW)
        GPIO.output(PIN3, GPIO.LOW)
        time.sleep(1)                  # Wait for 1 second

finally:
    # Cleanup: Resets all channels that have been set up by this script 
    # to INPUTS with no pull-up/down, preventing accidental shorts/damage.
    GPIO.cleanup()
