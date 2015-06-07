#!/usr/bin/python
#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#
# Adapted and refactored code from:
#
from time import sleep


class LcdDisplay(object):
    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80
    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00
    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00
    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00
    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, pin_e, pin_rs, pin_db_4, pin_db_5, pin_db_6, pin_db_7, pin_backlight, GPIO=None):
        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        if not GPIO:
            import RPi.GPIO as GPIO
        GPIO.setwarnings(False)

        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = [pin_db_4, pin_db_5, pin_db_6, pin_db_7]
        self.pin_light = pin_backlight
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)
        self.GPIO.setup(self.pin_light, GPIO.OUT)
        self.write_4_bits(0x33)  # initialization
        self.write_4_bits(0x32)  # initialization
        self.write_4_bits(0x28)  # 2 line 5x7 matrix
        self.write_4_bits(0x0C)  # turn cursor off 0x0E to enable cursor
        self.write_4_bits(0x06)  # shift cursor right
        self.display_control = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display_function = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.display_function |= self.LCD_2LINE
        # Initialize to default text direction (for romance languages)
        self.display_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write_4_bits(self.LCD_ENTRYMODESET | self.display_mode)  # set the entry mode
        self.clear()
        self.lines_number = 2

    def begin(self, cols, lines):
        if (lines > 1):
            self.lines_number = lines
            self.display_function |= self.LCD_2LINE

    def backlight_on(self):
        self.GPIO.output(self.pin_light, True)

    def backlight_off(self):
        self.GPIO.output(self.pin_light, False)

    def backlight_toggle(self):
        current = self.GPIO.input(self.pin_light)
        self.GPIO.output(self.pin_light, 1 if current == 0 else 0)

    def home(self):
        self.write_4_bits(self.LCD_RETURNHOME)  # set cursor position to zero
        self.delay_microseconds(3000)  # this command takes a long time!

    def clear(self):
        self.write_4_bits(self.LCD_CLEARDISPLAY)  # command to clear display
        self.delay_microseconds(3000)  # 3000 microsecond sleep, clearing the display takes a long time

    def set_cursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.lines_number:
            row = self.lines_number - 1  # we count rows starting w/0
        self.write_4_bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def no_display(self):
        """ Turn the display off (quickly) """
        self.display_control &= ~self.LCD_DISPLAYON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def display(self):
        """ Turn the display on (quickly) """
        self.display_control |= self.LCD_DISPLAYON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def no_cursor(self):
        """ Turns the underline cursor off """
        self.display_control &= ~self.LCD_CURSORON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def cursor(self):
        """ Turns the underline cursor on """
        self.display_control |= self.LCD_CURSORON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def no_blink(self):
        """ Turn the blinking cursor off """
        self.display_control &= ~self.LCD_BLINKON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink(self):
        """ Turn the blinking cursor on """
        self.display_control |= self.LCD_BLINKON
        self.write_4_bits(self.LCD_DISPLAYCONTROL | self.display_control)

    def display_left(self):
        """ These commands scroll the display without changing the RAM """
        self.write_4_bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scroll_display_right(self):
        """ These commands scroll the display without changing the RAM """
        self.write_4_bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT)

    def left_to_right(self):
        """ This is for text that flows Left to Right """
        self.display_mode |= self.LCD_ENTRYLEFT
        self.write_4_bits(self.LCD_ENTRYMODESET | self.display_mode)

    def right_to_left(self):
        """ This is for text that flows Right to Left """
        self.display_mode &= ~self.LCD_ENTRYLEFT
        self.write_4_bits(self.LCD_ENTRYMODESET | self.display_mode)

    def auto_scroll(self):
        """ This will 'right justify' text from the cursor """
        self.display_mode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write_4_bits(self.LCD_ENTRYMODESET | self.display_mode)

    def no_autoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.display_mode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write_4_bits(self.LCD_ENTRYMODESET | self.display_mode)

    def write_4_bits(self, bits, char_mode=False):
        """ Send command to LCD """
        self.delay_microseconds(1000)  # 1000 microsecond sleep
        bits = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)
        self.pulse_enable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4, 8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i - 4], True)
        self.pulse_enable()

    def delay_microseconds(self, microseconds):
        seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulse_enable(self):
        self.GPIO.output(self.pin_e, False)
        self.delay_microseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, True)
        self.delay_microseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, False)
        self.delay_microseconds(1)  # commands need > 37us to settle

    def _text_to_line(self, text):
        return text[0:20].ljust(20)

    def _echo_line(self, text):
        for char in text:
            self.write_4_bits(ord(char), True)

    def set_message(self, text):
        self.clear()
        """ Send string to LCD. Newline wraps to second line"""
        lines = text.split('\n')
        first_line = self._text_to_line(lines[0])
        second_line = self._text_to_line(lines[1]) if len(lines) > 1 else " " * 20

        self._echo_line(first_line)
        self.set_cursor(0, 1)
        self._echo_line(second_line)

    def set_first_line_messsage(self, text):
        self.set_cursor(0, 0)
        self._echo_line(text)

    def set_second_line_messsage(self, text):
        self.set_cursor(0, 1)
        self._echo_line(text)
