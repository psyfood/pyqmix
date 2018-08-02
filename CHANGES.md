2018-08-02
----------
* Add `config` module to `pyqmix.__all__`
* Remove Qmix SDK header directory config option
* Add convenience method `QmixPump.set_syringe_params_by_type()`
  to set syringe parameters by specifying a syringe type
* Set default flow and volume units when instantiation a `QmixPump`

2018-08-01
----------
* Support latest Qmix SDK
* Do not restore pump drive position counter by default
* Add convenience method `QmixPump.set_syringe_params_by_type()`
  to set syringe parameters by specifying a syringe type

2018-05-25
----------
* Support for a configuration file
* Don't do a blocking wait when calibrating pumps by default
* More example scripts
* Add support for several new Qmix SDK functions

2018-02-21
----------
* `QmixBus` gained `auto_open` and `auto_start` init parameters
* `QmixPump` gained `auto_enable` init parameter

2017-10-09
----------
* Convert `config.py` module to sub-package
* Add pump configurations to the new `config.pumps` module 
* Add `pump.init_pump()` convenience function for pump setup
* Add `pump.fill_syringes()` and `pump.empty_syringes` convenience functions

2017-10-05
----------
* Add `config.py` module

2017-10-04
----------
* Add valve `position` setter. The new property replaces the `current_position`
  property of `QmixValve` and `QmixExternalValve`.
* Split monolithic `interface.py` into device-specific submodules
