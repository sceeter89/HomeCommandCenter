from IGpioAdapter import IGpioAdapter
from ConfigParser import SafeConfigParser

class FakeGpioAdapter(IGpioAdapter):
    def _getCurrentConfig(self):
        config = SafeConfigParser()
        config.read('fakeGpio.cfg')

        return config

    def _getConfigValue(self, section, entry):
        config = self._getCurrentConfig()
        return config.get(section, entry)

    def _getBoolConfigValue(self, section, entry):
        config = self._getCurrentConfig()
        return config.getboolean(section, entry)

    def _setConfigValue(self, section, entry, value):
        config = self._getCurrentConfig()
        if config.has_section(section) == False:
            config.add_section(section)

        config.set(section, entry, value)

        with open('fakeGpio.cfg', 'wb') as configfile:
            config.write(configfile)

    def set_led_state(self, name, is_on):
        self._setConfigValue('led', name, is_on)

    def get_led_state(self, name):
        return self._getBoolConfigValue('led', name)

    def set_message(self, message):
        self._setConfigValue('lcdDisplay', 'message', message)

    def get_message(self):
        return self._getConfigValue('lcdDisplay', 'message')

    def get_display_backlight(self):
        return self._getBoolConfigValue('lcdDisplay', 'backlight')

    def set_display_backlight(self, is_on):
        self._setConfigValue('lcdDisplay', 'backlight', is_on)

    def get_alarm_armed(self):
        return self._getBoolConfigValue('alarm', 'armed')

    def get_alarm_alert(self):
        return self._getBoolConfigValue('alarm', 'alert')

