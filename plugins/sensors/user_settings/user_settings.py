from datetime import datetime

from yapsy.IPlugin import IPlugin

from api.sensor import Sensor


class UserSettings(Sensor, IPlugin):
    def __init__(self):
        super().__init__()

    def get_state(self):
        return {'holiday-mode': datetime(2015, 7, 14, 20, 0, 0) <= datetime.now() <= datetime(2015, 7, 21, 20, 0, 0)}
