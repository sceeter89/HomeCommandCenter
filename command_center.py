from api.exceptions import TerminateApplication

import time
from datetime import datetime
import logging
from yapsy.PluginManager import PluginManager

from api.sensor import Sensor
from api.motor import Motor

logging.basicConfig(level=logging.DEBUG)


def start_main_loop(sensors, motors):
    disabled_plugins = []
    while True:
        try:
            state = {
                'errors': [],
                'now': datetime.now()
            }
            for name, plugin in sensors:
                try:
                    state[name] = plugin.get_state()
                except Exception as e:
                    state['errors'].append(e)

            for name, plugin in motors:
                plugin.on_trigger(state)
        except TerminateApplication:
            break

        time.sleep(0.2)


def collect_all_plugins():
    # Load the plugins from the plugin directory.
    plugin_manager = PluginManager()
    plugin_manager.setPluginPlaces(['plugins/motors', 'plugins/sensors'])
    plugin_manager.collectPlugins()

    return plugin_manager.getAllPlugins()


def load_plugins(all_plugins):
    used_plugin_keys = set()

    motor_plugins = []
    sensor_plugins = []
    for plugin in all_plugins:
        logging.debug('Processing plugin {} <{}>...', plugin.name, type(plugin.plugin_object))

        if plugin.name in used_plugin_keys:
            logging.warning('Attempt to load already loaded plugin "{}" from "{}"', plugin.name, plugin.path)
            continue

        if isinstance(plugin.plugin_object, Motor):
            logging.debug("\tFound motor plugin.")
            motor_plugins.append((plugin.name, plugin.plugin_object))
        if isinstance(plugin.plugin_object, Sensor):
            key = plugin.details.get('core', None).get('key', None)
            logging.debug("\tFound sensor plugin with key: {}", key)
            sensor_plugins.append((plugin.name, plugin.plugin_object))

    return sensor_plugins, motor_plugins


def main():
    all_plugins = collect_all_plugins()
    motors, sensors = load_plugins(all_plugins)
    start_main_loop(sensors, motors)


if __name__ == "__main__":
    main()
