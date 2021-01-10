from adafruit_magtag.magtag import MagTag

magtag = MagTag()

magtag.add_text(
    text_font="Arial-18.bdf",
    text_position=(
        14,
        (magtag.graphics.display.height // 2),
    ),
    text_wrap=30,
)

magtag.set_text(
    "This is just some text to print out for testing stuff. This is more text. A bit.")

counter = 0

while True:
    counter += 1

    if counter > 1000:
        counter = 0
