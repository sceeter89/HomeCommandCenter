from yapsy.IPlugin import IPlugin
from api.motor import Motor
from helpers.diode import Diode


class GreenLed(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._diode = Diode(led_pin=18)
        self._diode.on()

    def on_trigger(self, current_state):
        if current_state['termination']:
            self._diode.off()
            return

        if 'weather' not in current_state:
            self._diode.on()
            return

        rain_chances = map(lambda x: x['chance_of_rain'], current_state['weather']['forecast'][:6])
        risky_forecasts = [x for x in rain_chances if x >= 10]

        if len(risky_forecasts) > 0:
            self._diode.toggle()
        else:
            self._diode.on()
