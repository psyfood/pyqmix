#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This simple usage example demonstrates how to initialize the pump system, fill
one syringe, and dispense a small volume multiple times.
"""

from pyqmix import QmixBus, QmixPump, config
import os.path as op
import time

# Location of Qmix device configuration and Qmix SDK DLLs.
configs_dir = op.abspath('./')
config_name = 'qmix_config'
dll_dir = op.normpath('D:/QmixSDK')

config.set_qmix_config(config_name=config_name, configs_dir=configs_dir)
config.set_qmix_dll_dir(dll_dir)

# Initialize the connection to the pump system.
bus = QmixBus()

# Initialize the first connected pump and perform a calibration move.
# Program execution is halted until the move is completed.
pump = QmixPump(index=0)
pump.calibrate(wait_until_done=True)

# Set pump and syringe parameters.
pump.set_flow_unit(prefix='milli', volume_unit='litres',
                   time_unit='per_second')
pump.set_volume_unit(prefix='milli', unit='litres')
pump.set_syringe_params_by_type(syringe_type='50 mL glass')

msg = ('The system is now calibrated. Please insert the syringe.\n\n'
       'Press RETURN when done.')
input(msg)

# Fill the syringe at a flow rate of 0.3 mL/s, and halt program execution
# until the filling is completed.
pump.generate_flow(-0.3, wait_until_done=True)

msg = ('The syringe is now filled. To start the experimental procedure, '
       'press RETURN.')
input(msg)

# Dispense 1 mL at a flow rate of 1 mL/s ten times, with a break of approx.
# 2 seconds between dispenses.
for i in range(10):
    pump.dispense(volume=1, flow_rate=1, wait_until_done=True)
    time.sleep(2)

msg = 'Stimulation is over. Press RETURN to quit.'
input(msg)
