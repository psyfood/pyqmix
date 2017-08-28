# -*- coding: utf-8 -*-
"""
Created on Wed Aug 09 15:14:54 2017

@author: 758099
"""
### DELAY TEST NEMESYS ###
#%%
from __future__ import division, print_function
from win32api import GetSystemMetrics
import numpy as np
import os
from psychopy import core, data, event, gui, visual 
from qmix import QmixBus, QmixPump, _QmixError, QmixDigitalIO
import pandas as pd
from pphelper.hardware import Trigger, Olfactometer


#%% INITIALIZE NEMESYS
qmix_bus = QmixBus()
qmix_bus.open()
qmix_bus.start()

pump_1 = QmixPump(index=0)
pump_1.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_1.set_volume_unit(prefix="milli", unit="litres")
pump_1.set_syringe_param(inner_diameter_mm=23.03, max_piston_stroke_mm=60)
pump_1.calibrate(blocking_wait=False)

pump_2 = QmixPump(index=1)
pump_2.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_2.set_volume_unit(prefix="milli", unit="litres")
pump_2.set_syringe_param(inner_diameter_mm=23.03, max_piston_stroke_mm=60)
pump_2.calibrate(blocking_wait=False)

pump_3 = QmixPump(index=2)
pump_3.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_3.set_volume_unit(prefix="milli", unit="litres")
pump_3.set_syringe_param(inner_diameter_mm=23.03, max_piston_stroke_mm=60)
pump_3.calibrate(blocking_wait=False)

pump_5 = QmixPump(index=4)
pump_5.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_5.set_volume_unit(prefix="milli", unit="litres")
pump_5.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
pump_5.calibrate(blocking_wait=False)

pump_6 = QmixPump(index=5)
pump_6.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_6.set_volume_unit(prefix="milli", unit="litres")
pump_6.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
pump_6.calibrate(blocking_wait=False)

#%% SET TRIGGERS
# CHANNEL 2
ch2_trig = Trigger(use_threads=False, test_mode=False, ni_task_name='channel_2', ni_lines='Dev1/PFI1:1')
ch2_trig.add_trigger('low_channel_2', 0)
ch2_trig.add_trigger('high_channel_2', 10)

#ch2_trig.select_trigger('low_channel_2')
#ch2_trig.select_trigger('high_channel_2')
#ch2_trig.trigger()

#%% CHANNEL 1
ch1_trig = Trigger(use_threads=False, test_mode=False, ni_lines='Dev1/PFI14')
ch1_trig.add_trigger('low_channel_1', 0)
ch1_trig.add_trigger('high_channel_1', 10)

#ch1_trig.select_trigger('low_channel_1')
#ch1_trig.select_trigger('high_channel_1')
#ch1_trig.trigger()

#%% AIR - OLFACTOMETER
air = Olfactometer()
air_channels = [0,0,0,0,0,0,1,0]
air.add_stimulus('air7', bitmask=air_channels, duration=0.1)
air.select_stimulus('air7')
air.stimulate()

#%%
air.select_stimulus('air4')
air.stimulate()
pump_6.dispense(0.07, 0.5)

#%% FILL THE SYRINGE
core.wait(8,8)
pump_6.aspirate(35, 1)

#%% DISPENSE LIQUID
#core.wait(8,8)
pump_5.dispense(2,5)
core.wait(1)
pump_5.valve.switch_position(position=0)

#%% TEST DELAY
core.wait(5,5)
ch2_trig.select_trigger('high_channel_2')
ch1_trig.select_trigger('high_channel_1')

pump_6.dispense(5,1)
ch2_trig.trigger()
ch1_trig.trigger()

#%% LOW TRIGGERS
ch2_trig.select_trigger('low_channel_2')
ch1_trig.select_trigger('low_channel_1')
ch2_trig.trigger()
ch1_trig.trigger()
#pump_6.set_fill_level(0,1)

#%% WASHING PUMPS
for i in range(10):
    pump_6.aspirate(30,1, blocking_wait=True)
    core.wait(2,2)
    pump_6.set_fill_level(0, 2.5, blocking_wait=True)


#%%
for _ in range(20):
    air.select_stimulus('air7')
    air.stimulate()
    pump_6.dispense(0.07,0.7)
    core.wait(0.3)
