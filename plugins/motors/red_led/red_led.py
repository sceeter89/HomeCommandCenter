from yapsy.IPlugin import IPlugin
from api.motor import Motor
from helpers.diode import Diode

LED_PIN = 15


class RedLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(LED_PIN)
        self.counter = 0

    def on_trigger(self, current_state):
        if self.counter % 2 != 0:
            return
        self.counter = (self.counter + 1) % 2

        if current_state['termination']:
            self._diode.on()
        elif 'alarm' in current_state and current_state['alarm']['alert']:
            self._diode.toggle()
