__author__ = 'yakuza'

import time
import logging
from yapsy.PluginManager import PluginManager

from api.sensor import Sensor
from api.motor import Motor

logging.basicConfig(level=logging.DEBUG)


def main():
    # Load the plugins from the plugin directory.
    plugin_manager = PluginManager()
    plugin_manager.setPluginPlaces(['plugins/motors', 'plugins/sensors'])
    plugin_manager.collectPlugins()

    motor_plugins = []
    sensor_plugins = []
    for plugin in plugin_manager.getAllPlugins():
        logging.debug('Processing plugin {} <{}>...', plugin.name, type(plugin.plugin_object))

        if isinstance(plugin.plugin_object, Motor):
            logging.debug("\tFound motor plugin.")
            motor_plugins.append(plugin)
        if isinstance(plugin.plugin_object, Sensor):
            key = plugin.details.get('core', None).get('key', None)
            logging.debug("\tFound sensor plugin with key: {}", key)
            sensor_plugins.append(plugin)

    while True:
        state = {
            'errors': []
        }
        for sensor_plugin in sensor_plugins:
            try:
                state[sensor_plugin.name] = sensor_plugin.plugin_object.get_state()
            except Exception as e:
                state['errors'].append(e)

        for motor_plugin in motor_plugins:
            motor_plugin.plugin_object.on_trigger(state)

        time.sleep(0.2)


if __name__ == "__main__":
    main()
