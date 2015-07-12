from yapsy.IPlugin import IPlugin
from api.motor import Motor
from helpers.LcdDisplay import LcdDisplay as DisplayDevice

PIN_RS = 15
PIN_E = 23
PIN_DB_4 = 18
PIN_DB_5 = 17
PIN_DB_6 = 27
PIN_DB_7 = 22
PIN_BACKLIGHT = 14


class LcdDisplay(Motor, IPlugin):
    def __init__(self):
        super().__init__()
        self._device = DisplayDevice(PIN_E, PIN_RS, PIN_DB_4, PIN_DB_5, PIN_DB_6, PIN_DB_7, PIN_BACKLIGHT)
        self._device.clear()
        self._device.backlight_on()
        self._last_set_minute = None

    def on_trigger(self, current_state):
        if current_state['termination']:
            if current_state['termination'][0]:
                self._device.set_message('Shut by: ' + str(current_state['termination'][0]))
            else:
                self._device.set_message('Closed by user.')

            return

        if "alarm" in current_state:
            if current_state['alarm']['armed']:
                self._device.set_message("Alarm is armed")
                self._device.backlight_off()
                return
            else:
                self._device.backlight_on()

        if current_state['now'].minute != self._last_set_minute:
            formatted_time = current_state['now'].strftime("%d.%m.%Y %H:%M")
            self._device.set_first_line_messsage(formatted_time)
            self._last_set_minute = current_state['now'].minute

        second_line = ""
        if "thermometer" in current_state:
            second_line = "%.1f %s" % (
            current_state['thermometer']['value'], current_state['thermometer']['unit_symbol'])

        if "hygrometer" in current_state:
            second_line += "  " + "%d%s" % (
            current_state['hygrometer']['value'], current_state['hygrometer']['unit_symbol'])

        if "barometer" in current_state:
            second_line += "  " + "%d%s" % (
            current_state['barometer']['value'], current_state['barometer']['unit_symbol'])

        self._device.set_second_line_messsage(second_line)
