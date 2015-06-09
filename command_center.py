from collections import namedtuple, defaultdict
from api.exceptions import TerminateApplication
from api.sensor import Sensor
from api.motor import Motor

import time
import logging
from datetime import datetime, timedelta
from yapsy.PluginManager import PluginManager

PluginDetails = namedtuple('PluginInfo', ['name', 'key', 'instance', 'wants_last_chance', 'path'])
ALLOWED_UNHANDLED_EXCEPTIONS_PER_PLUGIN = 10


class CoreApplication:
    def __init__(self, sensors, motors):
        self._motors = motors
        self._sensors = sensors
        self._disabled_plugins = set()
        self._runtime_stats = {
            'start_time': datetime.now(),
            'loop_counter': 0,
            'errors': defaultdict(list),
            'average_loop_duration': timedelta(seconds=0),
            'last_loop_duration': timedelta(seconds=0)
        }
        self._termination = None
        self._total_loops_duration = timedelta()

    def _process_sensors(self, state):
        for plugin in self._sensors:
            if plugin.key in self._disabled_plugins:
                continue

            try:
                state[plugin.key] = plugin.instance.get_state()
            except TerminateApplication as exception:
                self._termination = (plugin.key, type(plugin.instance), exception.reason)
            except KeyboardInterrupt:
                self._termination = (None, None, "User interruption")
            except Exception as exception:
                logging.debug('"%s" threw exception.', plugin.key, exc_info=exception)
                self._runtime_stats['errors'][plugin.key].append(exception)
                state['errors'].append((plugin.key, exception))

    def _process_motors(self, state):
        for plugin in self._motors:
            if plugin.key in self._disabled_plugins:
                continue

            try:
                plugin.instance.on_trigger(state)
            except TerminateApplication as exception:
                self._termination = (plugin.key, type(plugin.instance), exception.reason)
            except KeyboardInterrupt:
                self._termination = (None, None, "User interruption")
            except Exception as exception:
                logging.debug('"%s" threw exception.', plugin.key, exc_info=exception)
                self._runtime_stats['errors'][plugin.key].append(exception)
                state['errors'].append((plugin.key, exception))

    def _disable_failing_plugins(self):
        for key in self._runtime_stats['errors']:
            if key in self._disabled_plugins:
                continue

            if len(self._runtime_stats['errors'][key]) > ALLOWED_UNHANDLED_EXCEPTIONS_PER_PLUGIN:
                logging.warning('Disabling plugin due to repeating failures: %s', key)
                self._disabled_plugins.add(key)

    def _update_runtime_statistics(self, loop_duration):
        self._total_loops_duration += loop_duration
        self._runtime_stats['loop_counter'] += 1
        self._runtime_stats['average_loop_duration'] = self._total_loops_duration / self._runtime_stats['loop_counter']
        self._runtime_stats['last_loop_duration'] = loop_duration

    def _build_loop_state(self):
        return {
            'errors': [],
            'now': datetime.now(),
            'runtime': self._runtime_stats,
            'disabled_plugins': self._disabled_plugins,
            'termination': self._termination
        }

    def start_main_loop(self):
        while self._termination is None:
            try:
                loop_start = datetime.now()
                state = self._build_loop_state()
                self._process_sensors(state)
                self._process_motors(state)

                self._disable_failing_plugins()

                loop_stop = datetime.now()

                loop_duration = loop_stop - loop_start
                self._update_runtime_statistics(loop_duration)

                if len(self._disabled_plugins) == len(self._sensors) + len(self._motors):
                    logging.warning('All plugins have been disabled. Terminating application..')
                    break

                if state['errors']:
                    logging.warning('Current loop was interrupted by following exceptions: %s', repr(state['errors']))

                time.sleep(0.2)

            except KeyboardInterrupt:
                self._termination = (None, None, "User interruption")

        logging.info("Initiating shutdown procedure...")
        terminal_state = self._build_loop_state()
        for plugin in self._motors:
            if plugin.key in self._disabled_plugins or not plugin.wants_last_chance:
                continue

            try:
                plugin.instance.on_trigger(terminal_state)
            except Exception as exception:
                self._runtime_stats['errors'][plugin.key].append(exception)

        logging.info("Shutdown complete.")
        logging.info(repr(self._runtime_stats))


def collect_all_plugins():
    plugin_manager = PluginManager()
    plugin_manager.setPluginPlaces(['plugins/motors', 'plugins/sensors'])
    plugin_manager.collectPlugins()

    for plugin in plugin_manager.getAllPlugins():
        name = plugin.name
        key = plugin.details.get('Core', 'key')
        wants_last_chance = plugin.details.get('Core', 'last-chance', fallback='').lower() == "true"
        instance = plugin.plugin_object
        path = plugin.path
        yield PluginDetails(name, key, instance, wants_last_chance, path)


def load_plugins(all_plugins):
    used_plugin_keys = set()

    motor_plugins = []
    sensor_plugins = []
    for plugin in all_plugins:
        logging.debug('Processing plugin %s (%s) <%s>...', plugin.key, plugin.name, type(plugin.instance))

        if plugin.key in used_plugin_keys:
            logging.warning('Attempt to load already loaded plugin. Duplicate: name="%s", key="%s", path "%s"',
                            plugin.name, plugin.key, plugin.path)
            continue

        if isinstance(plugin.instance, Motor):
            logging.debug("\tFound motor plugin.")
            motor_plugins.append(plugin)
        if isinstance(plugin.instance, Sensor):
            logging.debug("\tFound sensor plugin with key: %s", plugin.key)
            sensor_plugins.append(plugin)

        used_plugin_keys.add(plugin.key)

    return sensor_plugins, motor_plugins


def main():
    all_plugins = collect_all_plugins()
    sensors, motors = load_plugins(all_plugins)
    app = CoreApplication(sensors=sensors, motors=motors)
    app.start_main_loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s][%(relativeCreated)d][%(levelname)s][%(module)s] %(message)s')
    try:
        main()
    except Exception as e:
        logging.error('Unexpected error occurred. If you believe issue is related to some bug in application, ' +
                      'please open issue with exception details at https://github.com/sceeter89/command-center/issues',
                      exc_info=e)
