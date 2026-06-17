from machine import ADC, Pin, SoftI2C
from dht import DHT22
from time import sleep
import json
import ssd1306
import network
from umqtt.simple import MQTTClient

# Connection pins for the temperature and humidity module
RED_LED_PIN = 2
ORANGE_LED_PIN = 17
GREEN_LED_PIN = 5
FAN_LED_PIN = 18

led_red = Pin(RED_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)
led_orange = Pin(ORANGE_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)
led_green = Pin(GREEN_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)
led_fan = Pin(FAN_LED_PIN, Pin.OUT, drive=Pin.DRIVE_0)

dht_device = DHT22(Pin(4, Pin.IN))

# Connection pin for the luminance module
adc_luminance_meter = ADC(Pin(34, Pin.IN))

# Connection pins for the motion detection module
motion_detector = Pin(16, Pin.IN)
motion_led = Pin(15, Pin.OUT, drive=Pin.DRIVE_0)

# Connection pins for the lcd display module (SSD1306)
display = ssd1306.SSD1306_I2C(128, 64, SoftI2C(sda=Pin(21), scl=Pin(22)))

wlan = network.WLAN(network.STA_IF)

client_id = "ESP_32_MQTT"
server = "mosquitto.nodered-fi.ipv64.net"
port = 1883
user = "FI"
password = "FI"
mqtt_client = MQTTClient(client_id, server, port, user, password, keepalive=0, ssl=False, ssl_params={})

def handle_led_fan_callback(topic, msg):

    topic = topic.decode('utf-8')

    converted_msg = json.loads(msg)

    if topic == "Met/Luefter/Timmel":
        led_fan.value(converted_msg == "true")

    pass

def mqtt_connect():
    mqtt_client.connect()
    mqtt_client.set_callback(handle_led_fan_callback)
    mqtt_client.subscribe("Met/Luefter/Timmel")


def do_connect():
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('FI24-Hotspot', 'BszWsw11#')
        while not wlan.isconnected():
            print("WLAN is not connected")
            pass

    print('network config:', wlan.ifconfig())


def send_mqtt_message(message):
    channel = "Met/FI/Timmel2007"
    mqtt_client.publish(channel, message)


def set_temperature_lights(red_on, orange_on, green_on):
    led_red.value(red_on)
    led_orange.value(orange_on)
    led_green.value(green_on)


def handle_temperature_led_lights(temp):
    if temp >= 25:
        set_temperature_lights(1, 0, 0)
    elif temp >= 25 and temp >= 20:
        set_temperature_lights(0, 1, 0)
    else:
        set_temperature_lights(0, 0, 1)


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


def display_text(lineOne, lineTwo, lineThree, lineFour, lineSix):
    display.fill(0)
    display.text(lineOne, 0, 0)
    display.text(lineTwo, 0, 10)
    display.text(lineThree, 0, 20)
    display.text(lineFour, 0, 30)
    display.text(lineSix, 0, 50)
    display.show()


def set_motion_led(motion):
    motion_led.value(motion == True)


def handle_lcd_data_display(temperature, humidity, motion, luminance, wlan):
    display_text(f"Temperatur: {temperature}", f"Humidity: {humidity}", f"Motion: {motion}", f"Lux: {luminance}", f"WLAN: {wlan}")


do_connect()
mqtt_connect()


while True:
    temp, humid = get_device_temperature_and_humidity()
    handle_temperature_led_lights(temp)
    motion = get_motion()
    luminance = get_luminance()
    set_motion_led(motion)
    handle_lcd_data_display(temp, humid, motion, luminance, wlan.isconnected())

    raw_json_object = {
        "Temperatur": temp,
        "Luftfeuchtigkeit": humid,
        "Bewegung": motion,
        "Helligkeit": luminance
    }

    json_object = json.dumps(raw_json_object)

    print(json_object)

    send_mqtt_message(json_object)
    mqtt_client.check_msg()
    sleep(1)
