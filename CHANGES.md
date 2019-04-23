Version 2019.1
------------------
* Handle non-existent configuration directory

Version 2018.12.13
------------------
* Update installation instructions
* Automated testing using Travis now also runs on Python 2.7 (only tested
  Python 3 before)
* `switch_valve_when_done` keyword argument is now available for all pumping
  operations
* Depend on `pypiwin32` instead of `pywin32`

Version 2018.11.07
------------------
* Report correct version number when installed from wheel.

Version 2018.11.05
------------------
* Updates to documentation
* Handle the case when a user requests to delete a non-existing configuration file.
* Update packages requirements to include `pywin32`.
* We now build universal wheels for both Python 2 and 3.
* Add support for Travis continuous integration tests on GitHub.

Version 2018.10.08a
-------------------
* Functionally identical to version 2018.10.08, but with additional docstrings for the config module.

Version 2018.10.08
------------------
This release includes all the changes listed below.

2018-10-06
----------
* Assume default location of Qmix configuration files (to avoid full path).   

2018-10-04
----------
* Rename `switch_valve_when_finished` keyword argument to 
  `switch_valve_when_done` to match `wait_until_done` wording
* Add `switch_valve_when_finished` keyword argument to
  `QmixPump.aspirate()` method
* Wait until the pumps have actually started operating before checking
  whether pumping has finished when using the `wait_until_done` kwarg.
* Imply `wait_until_done=True` when `switch_valve_when_done=True`
  keyword argument is specified.
* Improve auto-discovery of Qmix SDK DLLs

2018-09-13
----------
* Rename `blocking_wait` keyword argument to `wait_until_done`

2018-08-09
----------
* Add `QmixPump.fill()` and `empty()` methods
* `QmixPump` methods now raise on invalid volume and flow rate
  parameters
* Package specifications have been moved from `setup.py` to `setup.cfg`
* Fix bug when determining valid valve positions

2018-08-07
----------
* Fix reathedocs build

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
