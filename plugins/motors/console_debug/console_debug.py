import logging
from yapsy.IPlugin import IPlugin
from api.motor import Motor


class ConsoleDebug(Motor, IPlugin):
    _counter = 0
    _modulo = 20

    def on_trigger(self, current_state):
        if self._counter % self._modulo == 0:
            logging.debug(repr(current_state))

        self._counter += 1
