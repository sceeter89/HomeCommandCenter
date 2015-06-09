from helpers.diode import Diode

LED_PIN = 15


class RedLed(Diode):
    counter = 0

    def __init__(self):
        super().__init__(LED_PIN)

    def on_trigger(self, current_state):
        if self.counter % 2 != 0:
            return
        self.counter = (self.counter + 1) % 2

        if current_state['termination']:
            self._on()
        elif 'alarm' in current_state and current_state['alarm']['alert']:
            self._toggle()
