import RPi.GPIO as GPIO


class Diode:
    def __init__(self, led_pin):
        GPIO.setmode(GPIO.BCM)
        self.led_pin = led_pin
        GPIO.setup(self.led_pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.led_pin, 1)

    def off(self):
        GPIO.output(self.led_pin, 0)

    def toggle(self):
        current = GPIO.input(self.led_pin)
        GPIO.output(self.led_pin, 0 if current == 1 else 1)
