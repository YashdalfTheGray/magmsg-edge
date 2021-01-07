import board
import time
import ssl
import wifi
import socketpool
import adafruit_requests
import terminalio

from adafruit_magtag.magtag import MagTag


def get_battery_color(current_volts):
    battery_min = 3.5
    battery_max = 4.15
    battery_range_top = battery_max - battery_min
    third_of_battery_range = battery_range_top / 3.0
    top_third_range_bottom = battery_range_top - third_of_battery_range

    if (current_volts <= battery_min):
        return (255, 0, 0)
    elif (current_volts >= battery_max):
        return (0, 255, 0)

    if (((current_volts - battery_min) / battery_range_top) >= 0.67):
        position_abs = current_volts - (battery_min + top_third_range_bottom)
        position = position_abs / third_of_battery_range
        return (int(255.0 - (255.0 * position)), 255, 0)
    else:
        position_abs = current_volts - battery_min
        position = position_abs / top_third_range_bottom
        return (255, int(255.0 * position), 0)


def handle_buttons(magtag, messages, message_index):
    result = message_index

    if magtag.peripherals.button_a_pressed:
        if result > 0:
            result = result - 1 if result >= 1 else 0
            magtag.set_text(messages[result]["content"])
        magtag.peripherals.neopixel_disable = True
    elif magtag.peripherals.button_b_pressed:
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill((255, 255, 255))
    elif magtag.peripherals.button_c_pressed:
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill(
            get_battery_color(magtag.peripherals.battery)
        )
    elif magtag.peripherals.button_d_pressed:
        if result < (len(messages) - 1):
            result = result + \
                1 if result <= (len(messages) - 2) else (len(messages) - 1)
            magtag.set_text(messages[result]["content"])
        magtag.peripherals.neopixel_disable = True
    else:
        magtag.peripherals.neopixel_disable = True

    return result


try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

auth_header = {
    "Authorization": "Bearer " + secrets["server_token"]
}

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())


response = requests.request(
    "GET", secrets["server_address"], headers=auth_header)
messages = response.json()
print(messages)

magtag = MagTag()

magtag.add_text(
    text_font="Arial-18.bdf",
    text_position=(
        20,
        (magtag.graphics.display.height // 2) - 1,
    ),
    text_scale=1,
)

current_message_index = 0
magtag.set_text(messages[current_message_index]["content"])

buttons = magtag.peripherals.buttons
button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
timestamp = time.monotonic()

counter = 0

while True:
    current_message_index = handle_buttons(
        magtag, messages, current_message_index)

    counter += 1

    if (counter > 1000):
        counter = 0

    time.sleep(0.1)
