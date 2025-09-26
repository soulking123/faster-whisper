import time
import board
import neopixel

pixels1 = neopixel.Neopixel(board.D18, 15,brightness=1)
x=0

pixels1.fill((0,220,0))

pixels1[10] = (0,20,255)

time.sleep(4)
