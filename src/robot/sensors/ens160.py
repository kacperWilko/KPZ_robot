import sys
from pathlib import Path

import smbus2 as smbus

sys.modules["smbus"] = smbus

DFROBOT_PATH = (
    Path(__file__).resolve().parents[3]
    / "third_party"
    / "DFRobot_ENS160"
    / "python"
    / "raspberrypi"
)

if DFROBOT_PATH.exists():
    sys.path.insert(0, str(DFROBOT_PATH))
else:
    pass

from DFRobot_ENS160 import DFRobot_ENS160_I2C


class ENS160Sensor:
    def __init__(self, address=0x53, bus=1):
        self._ens = DFRobot_ENS160_I2C(i2c_addr=address, bus=bus)
        self._ens.begin()
        try:
            self._ens.setPWRMode(self._ens.ENS160_STANDARD_MODE)
        except AttributeError:
            pass

    def compensate(self, temperature_c, humidity_pct):
        try:
            self._ens.setTempAndHum(float(temperature_c), float(humidity_pct))
        except AttributeError:
            pass

    def _get(self, name):
        v = getattr(self._ens, name)
        return v() if callable(v) else v

    def read(self):
        aqi = int(self._get("get_AQI"))
        tvoc = int(self._get("get_TVOC_ppb"))
        eco2 = int(self._get("get_ECO2_ppm"))
        return {
            "aqi": aqi,
            "tvoc_ppb": tvoc,
            "eco2_ppm": eco2,
        }
