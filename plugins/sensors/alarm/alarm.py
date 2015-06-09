import RPi.GPIO as GPIO
from api.sensor import Sensor

ALARM_ARMED_PIN = 10
ALARM_ALERT_PIN = 9


class Alarm(Sensor):
    ITEMS_LIMIT = 8
    TRIGGER_THRESHOLD = 6
    DROP_THRESHOLD = 3

    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ALARM_ARMED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ALARM_ALERT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self._armed_readings = []
        self._alert_readings = []
        self._last_armed_result = False
        self._last_alert_result = False

    def _get_readings_state(self, readings, last_result):
        if len(readings) > self.ITEMS_LIMIT:
            readings.pop(0)

        high_readings = readings.count(True)

        if high_readings >= self.TRIGGER_THRESHOLD:
            return 1
        elif high_readings <= self.DROP_THRESHOLD:
            return 0
        else:
            return last_result

    def _get_armed_state(self):
        self._last_armed_result = self._get_readings_state(self._armed_readings, self._last_armed_result)
        return self._last_armed_result

    def _get_alert_state(self):
        self._last_alert_result = self._get_readings_state(self._alert_readings, self._last_alert_result)
        return self._last_alert_result

    def get_state(self):
        self._armed_readings.append(GPIO.input(ALARM_ARMED_PIN) == 1)
        self._alert_readings.append(GPIO.input(ALARM_ALERT_PIN) == 1)

        return {
            'armed': self._get_armed_state(),
            'alert': self._get_alert_state()
        }
