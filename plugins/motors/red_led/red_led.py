from helpers.diode import Diode

LED_PIN = 15


class RedLed(Diode):
    led_pin = LED_PIN
    counter = 0

    def on_trigger(self, current_state):
        if self.counter % 2 != 0:
            return
        self.counter = (self.counter + 1) % 2

        if current_state['termination']:
            self._on()
        elif 'alarm' in current_state and current_state['alarm']['alert']:
            self._toggle()
