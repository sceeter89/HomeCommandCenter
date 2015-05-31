__author__ = 'yakuza'
from datetime import datetime
import time

from api.motor import Motor

class ConsoleDebug(Motor):
    def on_trigger(self, current_state):
        print(datetime.now())
        print(repr(current_state))
        time.sleep(1)
