from machine import ADC, Pin, SoftI2C
from dht import DHT22
from time import sleep
import json
import ssd1306

# Connection pins for the temperature and humidity module
RED_LED_PIN = 2
ORANGE_LED_PIN = 17
GREEN_LED_PIN = 5

led_red = Pin(RED_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)
led_orange = Pin(ORANGE_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)
led_green = Pin(GREEN_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)

dht_device = DHT22(Pin(4, Pin.IN))

# Connection pin for the luminance module
adc_luminance_meter = ADC(Pin(34, Pin.IN))

# Connection pins for the motion detection module
motion_detector = Pin(16, Pin.IN)
motion_led = Pin(15, Pin.OUT, drive=Pin.DRIVE_0)

# Connection pins for the lcd display module (SSD1306)
display = ssd1306.SSD1306_I2C(128, 64, SoftI2C(sda=Pin(21), scl=Pin(22)))

def set_temperature_lights(red_on, orange_on, green_on):
    led_red.value(red_on)
    led_orange.value(orange_on)
    led_green.value(green_on)

def handle_temperatue_led_lights(temp):
    if temp >= 25:
        set_temperature_lights(1,0,0)
    elif temp >= 25 and temp >= 20:
        set_temperature_lights(0,1,0)
    else:
        set_temperature_lights(0,0,1)

def get_device_temperature_and_humidity():
    dht_device.measure()
    temp = dht_device.temperature()
    humid = dht_device.humidity()
    return temp, humid

def get_luminance():
    gamma = 0.7
    rl10 = 50
    ref_voltage = 3.3
    voltage = (adc_luminance_meter.read() / 4) / 1024 * ref_voltage
    resistance = 2000 * voltage / (1 - voltage / ref_voltage)
    return pow((rl10 * 1e3) * pow(10, gamma) / resistance, (1 / gamma))

def get_motion():
    return bool(motion_detector.value())

def display_text(lineOne,lineTwo,lineThree,lineFour):
    display.fill(0)
    display.text(lineOne, 0, 0)
    display.text(lineTwo, 0, 10)
    display.text(lineThree, 0, 30)
    display.text(lineFour, 0, 40)
    display.show()
    
def set_motion_led(motion):
    motion_led.value(motion == True)
    
def handle_lcd_data_display(temperature, humidity, motion, luminance):
    display_text(f"Temperatur: {temp}", f"Humidity: {humid}", f"Motion: {motion}", f"Lux: {luminance}")

while True:
    temp, humid = get_device_temperature_and_humidity()
    handle_temperatue_led_lights(temp)
    motion = get_motion()    
    luminance = get_luminance()
    set_motion_led(motion)
    handle_lcd_data_display(temperature, humidity, motion, luminance)
    
    raw_json_object = {
        "Temperatur": temp,
        "Luftfeuchtigkeit": humid,
        "Bewegung": motion,
        "Helligkeit": luminance
    }
    
    json_object = json.dumps(raw_json_object)
    
    print(json_object)
    sleep(1)