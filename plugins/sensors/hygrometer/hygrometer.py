from datetime import datetime, timedelta
import subprocess

from yapsy.IPlugin import IPlugin

from api.sensor import Sensor

SENSOR = 11  # Acceptable values: [11, 22, 2302]
PIN = 24
HUMIDITY_READ_CMD_FORMAT = 'python /usr/src/Adafruit_Python_DHT/examples/humidity_reader.py {sensor} {pin}'
HUMIDITY_READ_CMD = HUMIDITY_READ_CMD_FORMAT.format(sensor=SENSOR, pin=PIN)

UPDATE_INTERVAL = timedelta(minutes=5)


class Hygrometer(Sensor, IPlugin):
    def __init__(self):
        super().__init__()

        self.last_update_time = datetime.min
        self.cached_state = {}

    def get_state(self):
        if datetime.now() - self.last_update_time < UPDATE_INTERVAL:
            return self.cached_state
        humidity = subprocess.check_output(HUMIDITY_READ_CMD, shell=True).strip()

        value = {'value': int(humidity), 'unit': 'Percent', 'unit_symbol': '%'}
        self.cached_state = value
        self.last_update_time = datetime.now()
        return value
