from api.motor import Motor
from helpers.LcdDisplay import LcdDisplay as DisplayDevice

PIN_RS = 25
PIN_E = 24
PIN_DB_4 = 23
PIN_DB_5 = 17
PIN_DB_6 = 27
PIN_DB_7 = 22
PIN_BACKLIGHT = 3


class LcdDisplay(Motor):
    def __init__(self):
        self._device = DisplayDevice(PIN_E, PIN_RS, PIN_DB_4, PIN_DB_5, PIN_DB_6, PIN_DB_7, PIN_BACKLIGHT)
        self._device.clear()
        self._device.backlight_on()
        self._last_set_minute = None

    def on_trigger(self, current_state):
        if current_state['now'].minute != self._last_set_minute:
            formatted_time = current_state['now'].strftime("%d.%m.%Y %H:%M")
            self._device.set_first_line_messsage(formatted_time)
            self._last_set_minute = current_state['now'].minute

        if "thermometer" in current_state:
            second_line = "%.2f %s" % (current_state['thermometer']['value'], current_state['thermometer']['unit_symbol'])
            self._device.set_second_line_messsage(second_line)

