#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

PUMP_1 = OrderedDict()
PUMP_1['name'] = 'PUMP_1'
PUMP_1['index'] = 0
PUMP_1['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_1['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_1['syringe'] = OrderedDict(inner_diameter_mm=23.0329,
                         max_piston_stroke_mm=60)

PUMP_2 = OrderedDict()
PUMP_2['index'] = 1
PUMP_2['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_2['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_2['syringe'] = OrderedDict(inner_diameter_mm=23.0329,
                         max_piston_stroke_mm=60)

PUMP_3 = OrderedDict()
PUMP_3['index'] = 2
PUMP_3['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_3['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_3['syringe'] = OrderedDict(inner_diameter_mm=23.0329,
                         max_piston_stroke_mm=60)

PUMP_4 = OrderedDict()
PUMP_4['index'] = 3
PUMP_4['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_4['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_4['syringe'] = OrderedDict(inner_diameter_mm=32.5735,
                         max_piston_stroke_mm=60)

PUMP_5 = OrderedDict()
PUMP_5['index'] = 4
PUMP_5['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_5['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_5['syringe'] = OrderedDict(inner_diameter_mm=32.5735,
                         max_piston_stroke_mm=60)

PUMP_6 = OrderedDict()
PUMP_6['index'] = 5
PUMP_6['flow'] = OrderedDict(prefix="milli", volume_unit="litres",
                      time_unit="per_second")
PUMP_6['volume'] = OrderedDict(prefix="milli", unit="litres")
PUMP_6['syringe'] = OrderedDict(inner_diameter_mm=32.5735,
                         max_piston_stroke_mm=60)
