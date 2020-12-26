# magmsg-edge

A fridge magnet that shows messages, written in CircuitPython with the ESP microcontroller.

## Resources and notes

### General

- [Adafruit's MagTag guide](https://learn.adafruit.com/adafruit-magtag/overview)
- [Adafruit's CircuitPython guide](https://learn.adafruit.com/adafruit-magtag/overview-2)
- [Libraries and Drivers docs](https://circuitpython.readthedocs.io/projects/bundle/en/latest/drivers.html)

### Charging Circuitry

- The MCP73831 charging circuit uses the `PROG` pin with a resistor connected to ground to determine the charging current
- The charging current range varries from about 500mA (or 0.5A or 0.5C/s) while using a 2kΩ programming resistor to about 100mA (or 0.1A or 0.1C/s) while using a 10kΩ programming resistor
- The schematics say that we are using a 5.1kΩ resistor with the `PROG` port so that means that we are charging at 200mA (or 0.2A or 0.2C/s)
- [MagTag Schematics](https://cdn-learn.adafruit.com/assets/assets/000/096/946/original/adafruit_products_MagTag_sch.png?1605026160)
- [MCP73831 Datasheet](https://cdn.sparkfun.com/assets/learn_tutorials/6/9/5/MCP738312.pdf)
- [3.7v/4.2v Battery Discharge Profile](https://cdn-learn.adafruit.com/assets/assets/000/000/979/original/components_tenergydischarge.gif?1447976645)

### Troubleshooting

- [CircuitPython releases](https://github.com/adafruit/circuitpython/releases)
- [Latest CircuitPython]
