from collections import namedtuple
from api.exceptions import TerminateApplication
from api.sensor import Sensor
from api.motor import Motor

import time
import logging
from datetime import datetime, timedelta
from yapsy.PluginManager import PluginManager

PluginDetails = namedtuple('PluginInfo', ['name', 'key', 'instance', 'wants_last_chance', 'path'])
ALLOWED_UNHANDLED_EXCEPTIONS_PER_PLUGIN = 10


def start_main_loop(sensors, motors):
    disabled_plugins = set()
    total_loops_duration = timedelta()
    runtime_stats = {
        'start_time': datetime.now(),
        'loop_counter': 0,
        'errors': {},
        'average_loop_duration': timedelta(seconds=0),
        'last_loop_duration': timedelta(seconds=0)
    }
    termination = None
    while termination is None:
        loop_start = datetime.now()
        state = {
            'errors': [],
            'now': datetime.now(),
            'runtime': runtime_stats,
            'disabled_plugins': disabled_plugins,
            'termination': termination
        }
        for plugin in sensors:
            if plugin.key in disabled_plugins:
                continue

            try:
                state[plugin.name] = plugin.instance.get_state()
            except TerminateApplication as exception:
                termination = (plugin.key, type(plugin.instance), exception.reason)
            except KeyboardInterrupt:
                termination = (plugin.key, type(plugin.instance), "User interruption")
            except Exception as exception:
                runtime_stats['errors'].get(plugin.key, []).append(exception)
                state['errors'].append(exception)

        for plugin in motors:
            if plugin.key in disabled_plugins:
                continue
            try:
                plugin.instance.on_trigger(state)
            except TerminateApplication as exception:
                termination = (plugin.key, type(plugin.instance), exception.reason)
            except KeyboardInterrupt:
                termination = (plugin.key, type(plugin.instance), "User interruption")
            except Exception as exception:
                runtime_stats['errors'].get(plugin.key, []).append(exception)
                state['errors'].append(exception)

        loop_stop = datetime.now()
        loop_duration = loop_stop - loop_start
        total_loops_duration += loop_duration
        runtime_stats['loop_counter'] += 1
        runtime_stats['average_loop_duration'] = total_loops_duration.total_seconds() / runtime_stats[
            'loop_counter']
        runtime_stats['last_loop_duration'] = loop_duration

        for failing_plugin in runtime_stats['errors']:
            if failing_plugin in disabled_plugins:
                continue

            if len(runtime_stats['errors'][failing_plugin]) > ALLOWED_UNHANDLED_EXCEPTIONS_PER_PLUGIN:
                disabled_plugins.add(failing_plugin)

        if len(disabled_plugins) == len(sensors) + len(motors):
            logging.warning('All plugins have been disabled. Terminating application..')
            break

        time.sleep(0.2)

    logging.info("Initiating shutdown procedure...")
    terminal_state = {
        'now': datetime.now(),
        'runtime': runtime_stats,
        'disabled_plugins': disabled_plugins,
        'termination': termination
    }
    for plugin in motors:
        if plugin.key in disabled_plugins or not plugin.wants_last_chance:
            continue

        try:
            plugin.instance.on_trigger(terminal_state)
        except Exception as exception:
            runtime_stats['errors'].get(plugin.key, []).append(exception)

    logging.info("Shutdown complete.")
    logging.info(repr(runtime_stats))


def collect_all_plugins():
    # Load the plugins from the plugin directory.
    plugin_manager = PluginManager()
    plugin_manager.setPluginPlaces(['plugins/motors', 'plugins/sensors'])
    plugin_manager.collectPlugins()

    for plugin in plugin_manager.getAllPlugins():
        name = plugin.name
        key = plugin.details.get('core', {}).get('key', None)
        wants_last_chance = plugin.details.get('core', {}).get('last-chance', False).lower() == "true"
        instance = plugin.plugin_object
        path = plugin.path
        yield PluginDetails(name, key, instance, wants_last_chance, path)


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
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s][%(relativeCreated)d][%(levelname)s][%(module)s] %(message)s')
    try:
        main()
    except Exception as e:
        logging.error('Unexpected error occurred. If you believe issue is related to some bug in application, ' +
                      'please open issue with exception details at https://github.com/sceeter89/command-center/issues',
                      exc_info=e)
