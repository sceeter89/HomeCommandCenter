from collections import namedtuple
from api.exceptions import TerminateApplication

import time
from datetime import datetime
import logging
from yapsy.PluginManager import PluginManager

from api.sensor import Sensor
from api.motor import Motor

# logging.basicConfig(level=logging.DEBUG)
PluginDetails = namedtuple('PluginInfo', ['name', 'key', 'instance', 'path'])


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

    for plugin in plugin_manager.getAllPlugins():
        name = plugin.name
        key = plugin.details.get('core', {}).get('key', None)
        instance = plugin.plugin_object
        path = plugin.path
        yield PluginDetails(name, key, instance, path)


def load_plugins(all_plugins):
    used_plugin_keys = set()

    motor_plugins = []
    sensor_plugins = []
    for plugin in all_plugins:
        logging.debug('Processing plugin {} <{}>...', plugin.name, type(plugin.instance))

        if plugin.key in used_plugin_keys:
            logging.warning('Attempt to load already loaded plugin. Duplicate: name="{}", key="{}", path "{}"',
                            plugin.name, plugin.key, plugin.path)
            continue

        if isinstance(plugin.instance, Motor):
            logging.debug("\tFound motor plugin.")
            motor_plugins.append(plugin)
        if isinstance(plugin.instance, Sensor):
            logging.debug("\tFound sensor plugin with key: {}", plugin.key)
            sensor_plugins.append(plugin)

        used_plugin_keys.add(plugin.key)

    return sensor_plugins, motor_plugins


def main():
    all_plugins = collect_all_plugins()
    motors, sensors = load_plugins(all_plugins)
    start_main_loop(sensors, motors)


if __name__ == "__main__":
    main()
