import time
from robot.state import sensor_data
from robot.sensors.bme280 import BME280Sensor
from robot.sensors.ens160 import ENS160Sensor


def sensors_loop():
    bme = BME280Sensor()
    ens = ENS160Sensor()

    time.sleep(2)

    while True:
        try:
            bme_data = bme.read()

            ens.compensate(
                temperature_c=bme_data["temperature_c"],
                humidity_pct=bme_data["humidity_pct"],
            )

            ens_data = ens.read()

            sensor_data["bme280"] = bme_data
            sensor_data["ens160"] = ens_data
            sensor_data["ts"] = time.time()

            print("[SENSORS]", sensor_data)
        except Exception as e:
            print("[SENSORS] error:", e)

        time.sleep(15)




























