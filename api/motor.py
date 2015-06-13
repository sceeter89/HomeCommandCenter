import abc


class Motor:
    @abc.abstractmethod
    def on_trigger(self, current_state):
        """ This method will be called repeatedly, so corresponding motor's state can be updated properly.
            You should keep this method as fast as possible because any lags will affect overall performance
            of service.
            Current state contains entire system state, read-only, which is dict-like structure where key is name
            of sensor python class, and value is state of given sensor.
        """
        pass
