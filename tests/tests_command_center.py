from hamcrest import assert_that, only_contains
import unittest
from api.motor import Motor
from api.sensor import Sensor
from command_center import PluginDetails, load_plugins


class CommandCenterTests(unittest.TestCase):
    def test_if_motors_and_sensors_are_properly_identified(self):
        motor = PluginDetails("motor_name", "motor_key", Motor(), False, "motor_path")
        sensor = PluginDetails("sensor_name", "sensor_key", Sensor(), False, "sensor_path")
        all_plugins = [motor, sensor]

        sensors, motors = load_plugins(all_plugins)

        assert_that(motors, only_contains(motor))
        assert_that(sensors, only_contains(sensor))

    def test_if_only_unique_keys_are_inserted_all_others_are_ignored(self):
        motor1 = PluginDetails("motor_name", "motor_key", Motor(), False, "motor_path")
        motor2 = PluginDetails("motor_name", "motor_key", Motor(), False, "motor_path")
        all_plugins = [motor1, motor2]

        sensors, motors = load_plugins(all_plugins)

        assert_that(motors, only_contains(motor1))
