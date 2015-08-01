from yapsy.IPlugin import IPlugin

from api.sensor import Sensor

W1_DEVICE_ID = '28-000006285400'
DEVICE_W1_SLAVE_PATH = '/sys/bus/w1/devices/%s/w1_slave' % W1_DEVICE_ID


class Thermometer(Sensor, IPlugin):
    def __init__(self):
        super().__init__()

    def get_state(self):
        with open(DEVICE_W1_SLAVE_PATH, 'r') as f:
            content = f.read().strip()
        temperature = float(content[-5:]) / 1000

        return {'value': temperature, 'unit': 'Celsius', 'unit_symbol': 'C'}
