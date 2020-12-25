import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import neopixel
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

# load secrets
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


# setup pins and hardware
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
    esp, secrets, status_light
)

# setup IO callbacks for listening to a feed


def connected(client):
    print("Connected to Adafruit IO!")


def subscribe(client, userdata, topic, granted_qos):
    print("Listening for changes on relay feed...")


def unsubscribe(client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def disconnected(client):
    print("Disconnected from Adafruit IO!")


def on_message(client, feed_id, payload):
    print("Feed {0} received new value: {1}".format(feed_id, payload))


def on_feed_msg(client, topic, message):
    print(message)


# connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

# initialize MQTT interface with the esp interface
MQTT.set_socket(socket, esp)

# initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"],
    password=secrets["aio_key"],
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# connect the callback methods defined above to Adafruit IO
io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe
io.on_unsubscribe = unsubscribe
io.on_message = on_message

# connect to Adafruit IO
print("Connecting to Adafruit IO...")
feed_name = "messages"
io.connect()
io.add_feed_callback(feed_name, on_feed_msg)
io.subscribe(feed_name)
io.get(feed_name)

# loop looking for messages
while True:
    try:
        io.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        io.reconnect()
        continue
    time.sleep(60)
