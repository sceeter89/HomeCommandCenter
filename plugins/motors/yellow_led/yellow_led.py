from yapsy.IPlugin import IPlugin
from api.motor import Motor
from helpers.diode import Diode

LOW_TEMPERATURE_WARNING = 15
HIGH_TEMPERATURE_WARNING = 28


class YellowLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(led_pin=14)
        self.counter = 0

    def on_trigger(self, current_state):
        self.counter = (self.counter + 1) % 2
        if self.counter % 2 != 0:
            return

        if 'thermometer' in current_state:
            temperature = current_state['thermometer']['value']

            if temperature <= LOW_TEMPERATURE_WARNING or temperature >= HIGH_TEMPERATURE_WARNING:
                self._diode.toggle()
                return

        if current_state['disabled_plugins']:
            self._diode.on()
        else:
            self._diode.off()
