Please note, that this project is active work in progress and as such might not be stable or work as you expect. Documentation is not complete as well.

# Home Command Center
It's a plugin based software that run on your Raspberry Pi, constantly monitoring home state basing on multiple sensors
and triggering motors that may take some actions basing on current system state. For example sensors might be:
* Thermometer
* Alarm stand-by and alert mode
* Hygrometer

And motors:
* LCD Display
* Email / SMS notifier
* Air conditioner remote control

Please see [Wiki](https://github.com/sceeter89/command-center/wiki/Home%20Command%20Center) for further information.


## Running Command Center
There are few requirements that must be fulfilled for core application to run. Every motor and sensor may introduce
plugin specific dependencies. Application is know to run on:
* Raspberry Pi B+ and Python 3.2.3
* Kubuntu 14.10 and Python 3.4.2
* Python packages:
  * _yapsy_
  * _RPi.GPIO_ - for plugins accessing Raspberry Pi GPIO pins 

To run tests you will additionally need `pyhamcrest` package. Navigate in command line to `command_center` directory 
and type following command to run all tests:
```bash
python -m unittest discover tests/
```
