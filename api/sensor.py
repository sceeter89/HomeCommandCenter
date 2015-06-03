import abc
from yapsy.IPlugin import IPlugin


class Sensor(IPlugin):
    @abc.abstractmethod
    def get_state(self):
        """
        This method should return current state of sensor. Returned value should be python dict and deep copy of
        original value as it should never be modified by motor once returned.
        """
        pass
