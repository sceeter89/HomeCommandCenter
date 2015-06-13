from yapsy.IPlugin import IPlugin
from api.motor import Motor
from helpers.diode import Diode

LED_PIN = 18


class GreenLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(LED_PIN)
        self.counter = 0

    def on_trigger(self, current_state):
        if self.counter % 2 != 0:
            return
        self.counter = (self.counter + 1) % 2

        if 'weather' not in current_state:
            self._diode.on()
            return

        rain_chances = map(lambda x: x['chance_of_rain'], current_state['weather']['forecast'][:6])
        risky_forecasts = [x for x in rain_chances if x >= 10]

        if len(risky_forecasts) > 0:
            self._diode.toggle()
        else:
            self._diode.on()
