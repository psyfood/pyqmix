#!/usr/bin/env python

"""
This usage example demonstrates how to initialize the pump system, fill
one syringe with water and one with a salty solution, and embed the
salty stimulation in-between a continuous stream of water.
"""

from pyqmix import QmixBus, QmixPump, config
import os.path as op
from time import sleep

# Location of Qmix device configuration and Qmix SDK DLLs.
# Adjust as needed.
config_dir = op.abspath('./qmix_config')
dll_dir = op.normpath('D:/QmixSDK')

config.set_qmix_config_dir(config_dir)
config.set_qmix_dll_dir(dll_dir)

# Flow and volume units and dimensions of the syringes.
flow_unit = dict(prefix='milli',
                 volume_unit='litres',
                 time_unit='per_second')

volume_unit = dict(prefix='milli', unit='litres')

# The actual flow rates to use. Units as specified above (mL/s).
flow_rate = dict(fill=-0.3,
                 water=1.0,
                 salty=1.0)

# Initialize the connection to the pump system.
bus = QmixBus()

# Initialize pumps.
#
# We will later fill the syringe in the first pump with water and the syringe
# in the second pump with a salty aqueous solution.
pump = dict(water=QmixPump(index=0),
            salty=QmixPump(index=1))

for p_name, p in pump.items():
    p.set_flow_unit(**flow_unit)
    p.set_volume_unit(**volume_unit)
    p.set_syringe_params_by_type(syringe_type='50 mL glass')

# Fill the syringes and halt program execution until the filling is completed.
pump['water'].generate_flow(flow_rate['fill'])
pump['salty'].generate_flow(flow_rate['fill'], wait_until_done=True)

msg = ('The syringes are now filled. To start the experimental procedure, '
       'press RETURN.')
input(msg)

# Run a dispense cycle (water – salty – water) 10 times, with a break of
# approx. 5 s between stimulations.
for i in range(10):
    pump['water'].dispense(volume=1, flow_rate=flow_rate['water'],
                           wait_until_done=True)
    pump['salty'].dispense(volume=1, flow_rate=flow_rate['salty'],
                           wait_until_done=True)
    pump['water'].dispense(volume=2, flow_rate=flow_rate['water'],
                           wait_until_done=True)
    sleep(5)

msg = 'Stimulation is over. Press RETURN to quit.'
input(msg)
