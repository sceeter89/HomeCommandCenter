# Home Command Center
It's a plugin based software that run on your Raspberry Pi, constantly monitoring home state basing on multiple sensors
such as:
* 1-wire thermometer
* Alarm stand-by and alert mode

After states of all sensors are retrieved then all motors are triggered.
 
## Architecture
Service consists of:
* Core application
* Sensors
* Motors

*Sensor* - is basically anything that collects some information from environment. For instance it might be code that
reads temperature from 1-wire thermometer or humidity from hygrometer. There are two types of sensors: _custom_ and
_built-in_. Custom sensors are pluggable via [Yapsy](http://yapsy.sourceforge.net) library, and should be put in
`plugins/sensors` directory. For details on developing your own sensor take a look at _Development_ section.

Below you will find list of all _built-in_ sensors:
* `errors` - value is list of all exceptions that occured during current run. It's cleared every iteration.
* `now` - contains datetime of current loop start. It's identical for every motor.
* `disabled_plugins` - list containing keys of all plugins that were disabled because of exceeded number of failures.

*Motor* - motor is a plugin, that basing on current sensors' state and own internal state, should perform some actions.
 For example when temperature remains too high, air conditioner might be turned on to drop it.

### Application flow
Sensors, then motors, if too much fails then disabled and logged information about all exceptions. Conditions when
disabled.

## Development
### Sensors
Available sensors out of the box.
#### Writing custom sensor
### Motors
Available motors out of the box.
#### Wrtitin custom motor
