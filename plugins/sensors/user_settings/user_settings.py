from datetime import datetime

import redis
from yapsy.IPlugin import IPlugin

from api.sensor import Sensor

DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

REDIS_URL = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


def _string_to_holiday(holiday_string):
    holiday_string = holiday_string.decode('utf-8')
    start_string, stop_string = holiday_string.split('\t')
    start = datetime.strptime(start_string, DATETIME_FORMAT)
    stop = datetime.strptime(stop_string, DATETIME_FORMAT)

    return start, stop


class UserSettings(Sensor, IPlugin):
    def __init__(self):
        super().__init__()
        self.redis = redis.StrictRedis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB)

    def _get_holiday_mode(self):
        raw_holidays = self.redis.smembers('settings:holidays')
        if not raw_holidays:
            return False

        all_holidays = []
        for raw_holiday in raw_holidays:
            start, stop = _string_to_holiday(raw_holiday)
            all_holidays.append({'start': start, 'stop': stop})

        now = datetime.now()
        return any(x['start'] <= now <= x['stop'] for x in all_holidays)

    def get_state(self):
        return {'holiday-mode': self._get_holiday_mode()}
