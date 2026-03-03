from machine import Pin
from time import sleep
import random
import network

print("Start Program...")

switch_1 = Pin(2, Pin.IN)
switch_2 = Pin(4, Pin.IN)

led = Pin(15, Pin.OUT, drive=Pin.DRIVE_0)

swapper = 0

ap = network.WLAN(network.AP_IF)
ap.config(ssid='WIFI@DB')
ap.config(max_clients=10)
ap.active(True)

while True:
    print("New Cycle", switch_1.value(), switch_2.value(), led.value())
    
    if switch_1.value() == 1 and switch_2.value() == 1:
        led.value(1)
    elif switch_1.value() == 0 and switch_2.value() == 1:
        if swapper == 1:
            led.value(1)
            swapper = 0
        else:
            led.value(0)
            swapper = 1
    else:
        led.value(0)
    next_random = random.random()
    print("Random: ", next_random)
    
    sleep(next_random)
    