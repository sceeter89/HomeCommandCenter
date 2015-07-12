from distutils.core import setup

setup(
    name='command-center',
    version='0.9',
    packages=['', 'api', 'helpers', 'plugins.motors.red_led', 'plugins.motors.green_led', 'plugins.motors.yellow_led',
              'plugins.motors.lcd_display', 'plugins.motors.console_debug', 'plugins.motors.sms_notifications',
              'plugins.motors.email_notifications', 'plugins.sensors.alarm', 'plugins.sensors.barometer',
              'plugins.sensors.hygrometer', 'plugins.sensors.thermometer', 'plugins.sensors.weather_forecast',
              'services.user_settings'],
    url='https://github.com/sceeter89/command-center',
    license='The MIT License',
    author='Adam',
    author_email='sceeter@wp.pl',
    description='',
    requires=['bottle', 'yapsy']
)
