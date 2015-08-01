from datetime import datetime
import json

def _get_holiday_mode(redis):
    raw_holidays = redis.sscan_iter('holidays')
    holidays = []
    for raw_holiday in raw_holidays:
        holidays.append(json.loads(raw_holiday))

    now = datetime.now()
    return any(x['start'] <= now <= x['stop'] for x in holidays)

def get_holiday(holiday, redis):
    redis

def get_settings(redis):
    settings = {
        'holiday-mode': _get_holiday_mode(redis)
    }

    return settings
