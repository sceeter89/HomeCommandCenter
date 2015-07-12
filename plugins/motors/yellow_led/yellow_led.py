import time

from yapsy.IPlugin import IPlugin

from api.motor import Motor
from helpers.diode import Diode

LOW_TEMPERATURE_WARNING = 15
HIGH_TEMPERATURE_WARNING = 28


class YellowLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(led_pin=7)

    def on_trigger(self, current_state):
        if 'thermometer' in current_state:
            temperature = current_state['thermometer']['value']

            if temperature <= LOW_TEMPERATURE_WARNING or temperature >= HIGH_TEMPERATURE_WARNING:
                self._diode.toggle()
                return

        if 'barometer' in current_state:
            if current_state['barometer']['internal_temperature'] > 30:
                for _ in range(3):
                    self._diode.on()
                    time.sleep(0.05)
                    self._diode.off()
                return

        if current_state['disabled_plugins']:
            self._diode.on()
        else:
            self._diode.off()
