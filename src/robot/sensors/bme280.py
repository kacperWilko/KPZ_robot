import board
from adafruit_bme280 import basic as adafruit_bme280


class BME280Sensor:
    def __init__(self, address: int = 0x76):
        i2c = board.I2C()
        self._bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)

    def read(self):
        return {
            "temperature_c": round(float(self._bme.temperature), 1),
            "humidity_pct": round(float(self._bme.humidity), 1),
            "pressure_hpa": int(round(float(self._bme.pressure))),
        }
