import abc
import RPi.GPIO as GPIO
from api.motor import Motor


class Diode(Motor):
    led_pin = -1

    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)

    def _on(self):
        GPIO.output(self.led_pin, 1)

    def _off(self):
        GPIO.output(self.led_pin, 0)

    def _toggle(self):
        current = GPIO.input(self.led_pin)
        GPIO.output(self.led_pin, 0 if current == 1 else 1)

    @abc.abstractmethod
    def on_trigger(self, current_state):
        pass
