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
* Python 3.4+
* Kubuntu 14.10
* Python packages:
  * _yapsy_

To run tests you will additionally need `pyhamcrest` package. Navigate in command line to `command_center` directory 
and type following command to run all tests:
```bash
python -m unittest discover tests/
```
