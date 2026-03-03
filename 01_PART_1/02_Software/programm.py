from machine import ADC, Pin, SoftI2C
from dht import DHT22
from time import sleep
import json
import ssd1306
import network
import gc
import esp
esp.osdebug(None)
gc.collect()

pin = SoftI2C(sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 64, pin)

def switch_temp_lights(red, orange, green):
    Pin(2, Pin.OUT, drive=Pin.DRIVE_0).value(red) # red led
    Pin(17, Pin.OUT, drive=Pin.DRIVE_0).value(orange) # orange led
    Pin(5, Pin.OUT, drive=Pin.DRIVE_0).value(green) # green led

def set_lights_for_temp(temp):
    if temp >= 30:
        switch_temp_lights(1,0,0)
    elif temp >= 25 and temp >= 20:
        switch_temp_lights(0,1,0)
    else:
        switch_temp_lights(0,0,1)

def get_device_temp_and_humid():
    dht_device = DHT22(Pin(4, Pin.IN))
    dht_device.measure()
    temp = dht_device.temperature()
    humid = dht_device.humidity()
    return temp, humid

def get_luminance():
    gamma = 0.7
    rl10 = 50
    voltage = (ADC(Pin(34, Pin.IN)).read() / 4) / 1024 * 5
    resistance = 2000 * voltage / (1 - voltage / 5)
    return pow((rl10 * 1e3) * pow(10, gamma) / resistance, (1 / gamma))

def get_motion():
    return bool(Pin(16, Pin.IN).value())

def display_text(lineOne,lineTwo,lineThree,lineFour):
    display.fill(0)
    display.text(lineOne, 0, 0)
    display.text(lineTwo, 0, 10)
    display.text(lineThree, 0, 30)
    display.text(lineFour, 0, 40)
    display.show()

wlan = network.WLAN()
wlan.active(True)
wlan.connect('ssid', 'psk')

mqtt_server = 'mosquitto.nodered-fi.ipv64.net'
mqtt_user = 'FI'
mqtt_pass = 'FI'

last_message = 0
message_interval = 5

client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = b'Met/FI/Timmel'

def mqtt_connect():
    client = MQTTClient(
            client_id, 
            mqtt_server, 
            user=mqtt_user, 
            password=mqtt_pass)
    client.connect()
    print('Connected to %s MQTT broker' % (mqtt_server))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

def send_message(message):
    try:
        client.check_msg()
        client.publish(topic_pub, message)
        last_message = time.time()
    except OSError as e:
        restart_and_reconnect()

def can_send_message():
    return (time.time() - last_message) > message_interval

client = mqtt_connect()

while True:
    temp, humid = get_device_temp_and_humid()
    set_lights_for_temp(temp)
    motion = get_motion()    
    luminance = get_luminance()
    display_text("Temperatur: ", str(temp), "Luftfeuchtigkeit", str(humid))
    
    if motion:
        Pin(15, Pin.OUT, drive=Pin.DRIVE_0).value(1)
    else:
        Pin(15, Pin.OUT, drive=Pin.DRIVE_0).value(0)
    
    raw_json_object = {
        "Temperatur": temp,
        "Luftfeuchtigkeit": humid,
        "Bewegung": motion,
        "Helligkeit": luminance
    }
    
    json_object = json.dumps(raw_json_object)
    
    if can_send_message():
        send_message(json_object)
    
    print(json_object)
    sleep(1)