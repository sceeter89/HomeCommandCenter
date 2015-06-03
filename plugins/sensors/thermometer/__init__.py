from api.sensor import Sensor


class Thermometer(Sensor):
    def get_state(self):
        return {'value': 20.5, 'unit': 'Celsius', 'unit_symbol': 'C'}
