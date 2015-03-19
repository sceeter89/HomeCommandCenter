import RPi.GPIO as GPIO
from ConfigParser import ConfigParser

class Diodes:
	def __init__(self):
		config = ConfigParser()
		config.read('../configuration.ini')
		self.red_pin = config.getint('pins', 'led_red')
		self.yellow_pin = config.getint('pins', 'led_yellow')
		self.green_pin = config.getint('pins', 'led_green')
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.red_pin, GPIO.OUT)
		GPIO.setup(self.yellow_pin, GPIO.OUT)
		GPIO.setup(self.green_pin, GPIO.OUT)

	def red_on(self):
		GPIO.output(self.red_pin, 1)

	def red_off(self):
		GPIO.output(self.red_pin, 0)

	def yellow_on(self):
		GPIO.output(self.yellow_pin, 1)

	def yellow_off(self):
		GPIO.output(self.yellow_pin, 0)

	def green_on(self):
		GPIO.output(self.green_pin, 1)

	def green_off(self):
		GPIO.output(self.green_pin, 0)
	
	def green_toggle(self):
		current = GPIO.input(self.green_pin)
		GPIO.output(self.green_pin, 0 if current == 1 else 1)
	
	def red_toggle(self):
		current = GPIO.input(self.red_pin)
		GPIO.output(self.red_pin, 0 if current == 1 else 1)
	
	def yellow_toggle(self):
		current = GPIO.input(self.yellow_pin)
		GPIO.output(self.yellow_pin, 0 if current == 1 else 1)
