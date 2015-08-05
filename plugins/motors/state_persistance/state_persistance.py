import redis
from yapsy.IPlugin import IPlugin

from api.motor import Motor

REDIS_URL = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


class StatePersistor(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self.redis = redis.StrictRedis(host=REDIS_URL, port=REDIS_PORT, db=REDIS_DB)

    def _set_key_value(self, key, value):
        self.redis.set('system-state:*' + key, value)

    def on_trigger(self, current_state):

        if "termination" in current_state and current_state["termination"]:
            term_info = current_state["termination"]
            if term_info[0]:
                self._set_key_value('termination:author', term_info[0])
                self._set_key_value('termination:reason', term_info[2])
                return
        else:
            self._set_key_value('termination:author', None)
            self._set_key_value('termination:reason', None)

        if 'dht' in current_state:
            self._set_key_value('temperature', current_state['dht']['temperature']['value'])
            self._set_key_value('humidity', current_state['dht']['humidity']['value'])
        else:
            self._set_key_value('temperature', None)
            self._set_key_value('humidity', None)

        if 'barometer' in current_state:
            self._set_key_value('atmospheric_pressure', current_state['barometer']['value'])
            self._set_key_value('device_temperature', current_state['barometer']['internal_temperature'])
        else:
            self._set_key_value('atmospheric_pressure', None)
            self._set_key_value('device_temperature', None)

        if 'alarm' in current_state:
            self._set_key_value('alarm:armed', current_state['alarm']['armed'])
            self._set_key_value('alarm:alert', current_state['alarm']['alert'])
        else:
            self._set_key_value('alarm:armed', None)
            self._set_key_value('alarm:alert', None)
