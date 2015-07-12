from configparser import ConfigParser
from datetime import datetime, timedelta
from math import floor

from yapsy.IPlugin import IPlugin
import requests

from api.sensor import Sensor

UPDATE_INTERVAL = timedelta(minutes=30)


class Thermometer(Sensor, IPlugin):
    def __init__(self):
        super().__init__()
        config = ConfigParser()
        config.read('/etc/command_center/weather.ini')
        self.api_key = config.get('weather', 'api_key')
        self.api_url = config.get('weather', 'api_url')
        self.location_query = config.get('weather', 'location_query')

        self.last_update_time = datetime.min
        self.cached_state = {}

    def get_state(self):
        if datetime.now() - self.last_update_time < UPDATE_INTERVAL:
            return self.cached_state

        url_format = "{api_url}?q={query}&format=json&extra=isDayTime%2ClocalObsTime&" \
                     "num_of_days=2&fx24=yes&includelocation=yes&tp=3&showlocaltime=yes&key={api_key}"
        url = url_format.format(api_key=self.api_key, api_url=self.api_url, query=self.location_query)
        r = requests.get(url)

        response = r.json()

        current = response['data']['current_condition'][0]
        forecast = response['data']['weather']
        # Weather forecast contains 9 entries per day, 1st is cumulative, 2nd for 1:00, 3rd for 4:00 etc.. till 22:00

        forecast_entries = []
        current_hour_index = floor(datetime.now().hour / 3 + 1)

        if current_hour_index == 1:
            forecast_entries.extend(forecast[0]['hourly'][1:])
        elif current_hour_index == 8:
            forecast_entries.extend(forecast[1]['hourly'][1:])
        else:
            forecast_entries.extend(forecast[0]['hourly'][current_hour_index:])
            last_entry_index = 8 - len(forecast_entries) + 1
            forecast_entries.extend(forecast[1]['hourly'][1:last_entry_index])

        new_weather = {
            'current': {
                'cloud_cover': int(current['cloudcover']),
                'humidity': int(current['humidity']),
                'temperature': int(current['temp_C']),
                'felt_temperature': int(current['FeelsLikeC']),
                'visibility': int(current['visibility'])
            },
            'forecast': []
        }
        for entry in forecast_entries:
            new_weather['forecast'].append({
                'chance_of_rain': int(entry['chanceofrain']),
                'temperature': int(entry['tempC']),
                'felt_temperature': int(entry['FeelsLikeC']),
                'humidity': int(entry['humidity']),
                'cloud_cover': int(entry['cloudcover']),
                'visibility': int(entry['visibility'])
            }
            )

        self.cached_state = new_weather
        self.last_update_time = datetime.now()
        return new_weather
