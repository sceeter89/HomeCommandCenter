from helpers.diode import Diode

LED_PIN = 14
LOW_TEMPERATURE_WARNING = 15
HIGH_TEMPERATURE_WARNING = 28

class YellowLed(Diode):
    counter = 0

    def __init__(self):
        super().__init__(LED_PIN)

    def on_trigger(self, current_state):
        if self.counter % 2 != 0:
            return
        self.counter = (self.counter + 1) % 2

        if 'thermometer' in current_state:
            temperature = current_state['thermometer']['value']

            if temperature <= LOW_TEMPERATURE_WARNING or temperature >= HIGH_TEMPERATURE_WARNING:
                self._toggle()
                return

        if current_state['disabled_plugins']:
            self._on()
        else:
            self._off()




