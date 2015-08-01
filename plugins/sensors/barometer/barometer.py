from datetime import timedelta, datetime
import subprocess

from yapsy.IPlugin import IPlugin

from api.sensor import Sensor

PRESSURE_READ_CMD = '/usr/src/Adafruit-Raspberry-Pi-Python-Code/Adafruit_BMP085/pressure_reader.py'
UPDATE_INTERVAL = timedelta(minutes=5)


class Barometer(Sensor, IPlugin):
    def __init__(self):
        super().__init__()

        self.last_update_time = datetime.min
        self.cached_state = {}

    def get_state(self):
        if datetime.now() - self.last_update_time < UPDATE_INTERVAL:
            return self.cached_state
        readings = subprocess.check_output(PRESSURE_READ_CMD, shell=True).strip()
        temperature, pressure = readings.split()

        value = {'value': int(pressure), 'unit': 'hectopascal', 'unit_symbol': 'hPa',
                 'internal_temperature': float(temperature)}
        self.cached_state = value
        self.last_update_time = datetime.now()
        return value
