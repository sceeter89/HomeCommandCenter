import RPi.GPIO as GPIO
from ConfigParser import ConfigParser


class Alarm:
    def __init__(self):
        config = ConfigParser()
        config.read('../configuration.ini')
        self.armed_pin = config.getint('pins', 'alarm_armed')
        self.alert_pin = config.getint('pins', 'alarm_alert')
        GPIO.setup(self.armed_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.alert_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def isArmed(self):
        return GPIO.input(self.armed_pin) == 1

    def isAlert(self):
        return GPIO.input(self.alert_pin) == 1
