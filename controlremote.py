import serial 
import time

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

TIMEOUT = 1000

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD_RATE,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=TIMEOUT
    )

    print(f"Connected to {PORT} at {BAUD_RATE} baud.")
    time.sleep(2)
    message_to_send = "AC_ON16"
    # The message must be encoded to bytes before sending
    ser.write(message_to_send.encode()) 
    print(f"Sent: '{message_to_send}'")

    # 4. Read response from the ESP
    time.sleep(0.1) # Give the ESP a moment to respond
except(e):
    print(e)

