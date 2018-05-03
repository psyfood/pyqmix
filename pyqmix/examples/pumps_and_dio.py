#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path as op
from pyqmix import QmixBus, QmixPump, QmixDigitalIO

dll_dir = op.normpath('C:\\Users\\758099.INTERN\\AppData\\Local\\QmixSDK')
config_dir = op.normpath('C:\\Users\\758099.INTERN\\Desktop\\neMESYS\\'
                         'config_qmix')

bus = QmixBus(config_dir=config_dir, dll_dir=dll_dir)
bus.open()
bus.start()

pump_0 = QmixPump(index=0)
pump_1 = QmixPump(index=1)
pump_2 = QmixPump(index=2)
pump_3 = QmixPump(index=3)

pump_0.enable()
pump_1.enable()
pump_2.enable()
pump_3.enable()

pump_0.set_flow_unit(prefix="milli", volume_unit="litres",
                     time_unit="per_second")
pump_1.set_flow_unit(prefix="milli", volume_unit="litres",
                     time_unit="per_second")
pump_2.set_flow_unit(prefix="milli", volume_unit="litres",
                     time_unit="per_second")
pump_3.set_flow_unit(prefix="milli", volume_unit="litres",
                     time_unit="per_second")

pump_0.set_volume_unit(prefix="milli", unit="litres")
pump_1.set_volume_unit(prefix="milli", unit="litres")
pump_2.set_volume_unit(prefix="milli", unit="litres")
pump_3.set_volume_unit(prefix="milli", unit="litres")

pump_0.set_syringe_params()
pump_1.set_syringe_params(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
pump_2.set_syringe_params()
pump_3.set_syringe_params()

ch0 = QmixDigitalIO(index=0)
ch1 = QmixDigitalIO(index=1)
ch2 = QmixDigitalIO(index=2)
ch3 = QmixDigitalIO(index=3)
ch4 = QmixDigitalIO(index=4)
ch5 = QmixDigitalIO(index=5)
ch6 = QmixDigitalIO(index=6)
ch7 = QmixDigitalIO(index=7)

pump_0.calibrate(blocking_wait=False)
pump_1.calibrate(blocking_wait=False)
pump_2.calibrate(blocking_wait=False)
pump_3.calibrate(blocking_wait=False)
