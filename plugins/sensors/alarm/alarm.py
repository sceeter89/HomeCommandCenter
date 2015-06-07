import RPi.GPIO as GPIO
from api.sensor import Sensor

ALARM_ARMED_PIN = 10
ALARM_ALERT_PIN = 9


class Alarm(Sensor):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ALARM_ARMED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ALARM_ALERT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def get_state(self):
        return {
            'armed': GPIO.input(ALARM_ARMED_PIN) == 1,
            'alert': GPIO.input(ALARM_ALERT_PIN) == 1
        }
