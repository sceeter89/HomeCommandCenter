import logging
import pprint

from yapsy.IPlugin import IPlugin

from api.motor import Motor


class ConsoleDebug(Motor, IPlugin):
    _modulo = 20

    def on_trigger(self, current_state):
        if current_state['runtime']['loop_counter'] % self._modulo == 0:
            logging.debug(pprint.pformat(current_state))
