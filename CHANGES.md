2017-10-09
----------
* Convert `config.py` module to sub-package
* Add pump configurations to the new `config.pumps` module 
* Add `pump.init_pump()` convenience function for pump setup

2017-10-05
----------
* Add `config.py` module

2017-10-04
----------
* Add valve `position` setter. The new property replaces the `current_position`
  property of `QmixValve` and `QmixExternalValve`.
* Split monolithic `interface.py` into device-specific submodules
