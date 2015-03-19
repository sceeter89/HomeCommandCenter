class IGpioAdapter:
    def set_led_state(self, name, is_on):
        pass

    def set_message(self, message):
        pass

    def get_led_state(self, name):
        pass

    def get_message(self):
        pass

    def get_display_backlight(self):
        pass

    def set_display_backlight(self, is_on):
        pass

    def get_alarm_armed(self):
        pass

    def get_alarm_alert(self):
        pass
