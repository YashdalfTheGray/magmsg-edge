import alarm
import board
import time
import ssl
import wifi
import socketpool
import adafruit_requests

from adafruit_magtag.magtag import MagTag

TENTH_OF_A_SECOND = 0.1
TWO_MINUTES_IN_TENTH_SECONDS = 1200
SIX_HOURS_IN_SECONDS = 21600


def sortFunc(elem):
    return elem["createdAt"]


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


try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


auth_header = {
    "Authorization": "Bearer " + secrets["server_token"]
}
sleep_timer = TWO_MINUTES_IN_TENTH_SECONDS
counter = 0
button_a_alarm = alarm.pin.PinAlarm(pin=board.D15, value=False)
button_d_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False)


print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)


pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
response = requests.request(
    "GET", secrets["server_address"], headers=auth_header
)
messages = response.json()
messages.sort(key=sortFunc)
print(messages)

magtag = MagTag()

magtag.add_text(
    text_font="Arial-18.bdf",
    text_position=(
        14,
        (magtag.graphics.display.height // 2),
    ),
    text_wrap=20,
)

current_message_index = len(messages) - 1
magtag.set_text(messages[current_message_index]["content"])

while True:
    if magtag.peripherals.button_a_pressed:
        if current_message_index > 0:
            current_message_index = current_message_index - \
                1 if current_message_index >= 1 else 0
            magtag.set_text(messages[current_message_index]["content"])
        magtag.peripherals.neopixel_disable = True
        counter = 0

    elif magtag.peripherals.button_b_pressed:
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill((255, 255, 255))
        counter = 0

    elif magtag.peripherals.button_c_pressed:
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill(
            get_battery_color(magtag.peripherals.battery)
        )
        counter = 0

    elif magtag.peripherals.button_d_pressed:
        if current_message_index < (len(messages) - 1):
            current_message_index = current_message_index + \
                1 if current_message_index <= (
                    len(messages) - 2) else (len(messages) - 1)
            magtag.set_text(messages[current_message_index]["content"])
        magtag.peripherals.neopixel_disable = True
        counter = 0

    else:
        magtag.peripherals.neopixel_disable = True
        counter += 1

    if counter > sleep_timer:
        break

    time.sleep(TENTH_OF_A_SECOND)

alarm.exit_and_deep_sleep_until_alarms(
    button_a_alarm,
    button_d_alarm,
    alarm.time.TimeAlarm(
        monotonic_time=time.monotonic() + SIX_HOURS_IN_SECONDS
    )
)
