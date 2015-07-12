from yapsy.IPlugin import IPlugin

from api.motor import Motor
from helpers.diode import Diode


class RedLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(led_pin=25)

    def on_trigger(self, current_state):
        if current_state['termination']:
            self._diode.on()
        elif 'alarm' in current_state and current_state['alarm']['alert']:
            self._diode.toggle()
        else:
            self._diode.off()
