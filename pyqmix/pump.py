#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
import atexit
from cffi import FFI
from collections import OrderedDict

if sys.version_info[0] < 3:
    # Python 2 compatibility; requires `future` package.
    from builtins import bytes

from . import config
from .valve import QmixValve
from .tools import CHK
from .headers import PUMP_HEADER


class QmixPump(object):
    """
    Qmix pump interface.
    """
    def __init__(self, index, name='', external_valves=None,
                 restore_drive_pos_counter=False,
                 auto_enable=True):
        """
        Parameters
        ----------
        index : int
            Index of the pump to access. It is related with the config files.
            First pump has ``index=0``, second has ``index=1`` and so on.
            Takes precedence over the `name` parameter.

        name : str
            The name of the pump.

        restore_drive_pos_counter : bool
            Whether to restore the pump drive position counter from the pyqmix
            config file.

        auto_enable : bool
            Whether to enable (i.e., activate) the pump on object instantiation.

        """
        cfg = config.read_config()
        dll_dir = cfg.get('qmix_dll_dir', None)
        if dll_dir is None:
            self.dll_file = 'labbCAN_Pump_API.dll'
        else:
            self.dll_file = os.path.join(dll_dir, 'labbCAN_Pump_API.dll')

        self._ffi = FFI()
        self._ffi.cdef(PUMP_HEADER)
        self._dll = self._ffi.dlopen(self.dll_file)

        self.index = index
        self._name = name

        self._handle = self._ffi.new('dev_hdl *', 0)
        self._call('LCP_GetPumpHandle', self.index, self._handle)

        self._flow_rate_max = self._ffi.new('double *')
        self._p_fill_level = self._ffi.new('double *')
        self._p_dosed_volume = self._ffi.new('double *')
        self._p_flow_rate = self._ffi.new('double *')

        self._p_flow_prefix = self._ffi.new('int *')
        self._p_flow_volume_unit = self._ffi.new('int *')
        self._p_flow_time_unit = self._ffi.new('int *')

        self._p_volume_prefix = self._ffi.new('int *')
        self._p_volume_unit = self._ffi.new('int *')
        self._p_volume_max = self._ffi.new('double *')

        # Syringe dimensions.
        self._p_inner_diameter_mm  = self._ffi.new('double *')
        self._p_max_piston_stroke_mm = self._ffi.new('double *')

        self._p_drive_pos_counter = self._ffi.new('long *')

        self._valve_handle = self._ffi.new('dev_hdl *', 0)
        self._call('LCP_GetValveHandle', self._handle[0], self._valve_handle)
        self.valve = QmixValve(handle=self._valve_handle)

        if self.is_in_fault_state:
            self.clear_fault_state()
        if not self.is_enabled:
            self.enable()

        if external_valves is None:
            self.ext_valves = dict()
        else:
            self.ext_valves = external_valves

        self.auto_enable = auto_enable
        if self.auto_enable:
            self.enable()

        try:  # Try to restore settings from configuration file.
            pump_config = cfg['pumps'][self.index]

            # We get back CommentedOrderedMap's, so convert to dicts.
            volume_unit = dict(pump_config['volume_unit'])
            flow_unit = dict(pump_config['flow_unit'])
            syringe_params = dict(pump_config['syringe_params'])

            name = pump_config['name']

            if restore_drive_pos_counter:
                drive_pos_counter = pump_config['drive_pos_counter']
            else:
                drive_pos_counter = self.drive_pos_counter

            if self._name == '':
                self._name = name

            self.volume_unit = volume_unit
            self.flow_unit = flow_unit
            self.syringe_params = syringe_params
            self.drive_pos_counter = drive_pos_counter
        except KeyError:  # Write default values to configuration file.
            self.set_flow_unit()
            self.set_volume_unit()

            config.add_pump(self.index)
            config.set_pump_name(self.index, self._name)
            config.set_pump_volume_unit(self.index, **self.volume_unit)
            config.set_pump_flow_unit(self.index, **self.flow_unit)
            config.set_pump_syringe_params(self.index, **self.syringe_params)
            config.set_pump_drive_pos_counter(self.index,
                                              self.drive_pos_counter)

        atexit.register(self.save_drive_pos_counter)

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        return CHK(r)

    @property
    def name (self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        config.set_pump_name(self.index, name)

    @property
    def is_enabled(self):
        """
        Query if pump drive is enabled.

        Only if the pump drive is enabled it is possible to pump fluid.

        Returns
        -------
        int
            1 - Pump drive is enabled, pumping is possible
            0 - Pump drive is disabled - pump head is free running

        """
        return self._call('LCP_IsEnabled', self._handle[0])

    def enable(self):
        """
        Enable the pump.

        """
        self._call('LCP_Enable', self._handle[0])

    def disable(self):
        """
        Deactivate the pump drive.

        """
        return self._call('LCP_Disable', self._handle[0])

    @property
    def is_in_fault_state(self):
        """
        Check if pump is in a fault state.

        If the device is in fault state then it is necessary to call
        :func:`qmix.QmixPump.clear_fault_state``, followed by a call to
        :func:`QmixPump.enable` to enable the pump.

        Returns
        -------
        int
            1 - Pump is in fault state
            0 - Pump is not in fault state

        """
        return self._call('LCP_IsInFaultState', self._handle[0])

    def clear_fault_state(self):
        """
        Clear fault condition.

        Clears the last fault and resets the
        device to an error-free state. If
        `qmix.QmixPump.is_in_fault_state`
        indicates that device is in fault state, then this method may resolve
        this problem.
        If the device is still in fault state after this method was called,
        we have to assume that a serious failure occurred.

        """
        self._call('LCP_ClearFault', self._handle[0])

    @property
    def is_calibration_finished(self):
        """
        Check if calibration is finished still ongoing.

        Returns
        -------
        bool
            True - Device calibration has finished/was perfomed
            False - Device is calibrating

        """
        r = self._call('LCP_IsCalibrationFinished', self._handle[0])
        if r == 0:
            return False
        else:
            return True

    def calibrate(self, blocking_wait=False):
        """
        Executes a reference move for a syringe pump.

        .. warning::     Executing the calibration move with a syringe
                         fitted on the device may cause damage to the
                         syringe.

        Parameters
        ----------
        blocking_wait : bool
            Whether to block further program execution until done.

        """
        self._call('LCP_SyringePumpCalibrate', self._handle[0])

        if blocking_wait:
            while not self.is_calibration_finished:
                time.sleep(0.0005)

    @property
    def n_pumps(self):
        """
        The number of dosing units.

        Returns
        -------
        int
            Number of detected pump devices

        """
        return self._call('LCP_GetNoOfPumps')

    def set_volume_unit(self, prefix='milli', unit='litres'):
        """
        Set the default volume unit.

        All parameters of subsequent dosing method calls are given in this new
        unit.

        Parameters
        ----------
        prefix : str
            The prefix of the SIunit:
            ``centi``, ``deci``, ``mircro``, ``milli``, ``unit``.

        unit : str
            The volume unit identifier: ``litres``.

        """
        self._call('LCP_SetVolumeUnit', self._handle[0],
                   getattr(self._dll, prefix.upper()),
                   getattr(self._dll, unit.upper()))

        config.set_pump_volume_unit(self.index, prefix=prefix, unit=unit)

    def get_volume_unit(self):
        """
        Return the currently set default volume unit.

        Returns
        -------
        OrderedDict
            A dictionary with the keys `prefix` and `unit`.

        """
        self._call('LCP_GetVolumeUnit', self._handle[0],
                   self._p_volume_prefix, self._p_volume_unit)

        if self._p_volume_prefix[0] == self._dll.MICRO:
            prefix = 'micro'
        elif self._p_volume_prefix[0] == self._dll.MILLI:
            prefix = 'milli'
        elif self._p_volume_prefix[0] == self._dll.CENTI:
            prefix = 'centi'
        elif self._p_volume_prefix[0] == self._dll.DECI:
            prefix = 'deci'
        else:
            raise RuntimeError('Invalid volume unit prefix retrieved.')

        if self._p_volume_unit[0] == self._dll.LITRES:
            unit = 'litres'
        else:
            raise RuntimeError('Invalid flow volume unit retrieved.')

        return OrderedDict([('prefix', prefix),
                            ('unit', unit)])

    @property
    def volume_unit(self):
        """
        The currently set default volume unit.

        Returns
        -------
        OrderedDict
            A dictionary with the keys `prefix` and `unit`.

        """
        return self.get_volume_unit()

    @volume_unit.setter
    def volume_unit(self, volume_unit):
        self.set_volume_unit(**volume_unit)

    @property
    def volume_max(self):
        self._call('LCP_GetVolumeMax', self._handle[0], self._p_volume_max)
        return self._p_volume_max[0]

    def set_flow_unit(self, prefix='milli', volume_unit='litres',
                      time_unit='per_second'):
        """
        Set the flow unit for a certain pump.

        The flow unit defines the unit to be used for all flow values passed to
        API functions or retrieved from API functions.

        Parameters
        ----------
        prefix : str
            The prefix of the SI unit:
            ``centi``, ``deci``, ``milli``, ``micro``.

        volume_unit : str
            The volume unit identifier: ``litres``.

        time_unit : str
            The time unit (denominator) of the velocity unit:
            ``per_hour``, ``per_minute``, ``per_second``.

        """
        self._call('LCP_SetFlowUnit', self._handle[0],
                   getattr(self._dll, prefix.upper()),
                   getattr(self._dll, volume_unit.upper()),
                   getattr(self._dll, time_unit.upper()))

        config.set_pump_flow_unit(self.index, prefix=prefix,
                                  volume_unit=volume_unit, time_unit=time_unit)

    def get_flow_unit(self):
        """
        Return the currently set flow unit.

        Returns
        -------
        OrderedDict
            A dictionary with the keys `prefix`, `volume_unit`, and
            `time_unit`.

        """
        self._call('LCP_GetFlowUnit', self._handle[0], self._p_flow_prefix,
                   self._p_flow_volume_unit, self._p_flow_time_unit)

        if self._p_flow_prefix[0] == self._dll.MICRO:
            prefix = 'micro'
        elif self._p_flow_prefix[0] == self._dll.MILLI:
            prefix = 'milli'
        elif self._p_flow_prefix[0] == self._dll.CENTI:
            prefix = 'centi'
        elif self._p_flow_prefix[0] == self._dll.DECI:
            prefix = 'deci'
        else:
            raise RuntimeError('Invalid flow unit prefix retrieved.')

        if self._p_flow_volume_unit[0] == self._dll.LITRES:
            volume_unit = 'litres'
        else:
            raise RuntimeError('Invalid flow volume unit retrieved.')

        if self._p_flow_time_unit[0] == self._dll.PER_SECOND:
            time_unit = 'per_second'
        elif self._p_flow_time_unit[0] == self._dll.PER_MINUTE:
            time_unit = 'per_minute'
        elif self._p_flow_time_unit[0] == self._dll.PER_HOUR:
            time_unit = 'per_hour'
        else:
            raise RuntimeError('Invalid flow time unit retrieved.')

        return OrderedDict([('prefix', prefix),
                            ('volume_unit', volume_unit),
                            ('time_unit', time_unit)])

    @property
    def flow_unit(self):
        """
        The currently set flow unit.

        Returns
        -------
        OrderedDict
            A dictionary with the keys `prefix`, `volume_unit`, and
            `time_unit`.
        """
        return self.get_flow_unit()

    @flow_unit.setter
    def flow_unit(self, flow_unit):
        self.set_flow_unit(**flow_unit)

    def set_syringe_params(self, inner_diameter_mm=32.5735,
                           max_piston_stroke_mm=60):
        """
        Set syringe properties.

        If you change the syringe in one device, you need to setup the new
        syringe parameters to get proper conversion of flow rate und volume
        units.

        Parameters
        ----------
        inner_diameter_mm : float
            Inner diameter of the syringe tube in millimetres.

        max_piston_stroke_mm : float
            The maximum piston stroke defines the maximum position the piston
            can be moved to before it slips out of the syringe tube.
            The maximum piston stroke limits the maximum travel range of the
            syringe pump pusher.

        """
        self._call('LCP_SetSyringeParam', self._handle[0], inner_diameter_mm,
                   max_piston_stroke_mm)

        config.set_pump_syringe_params(
            self.index,
            inner_diameter_mm=inner_diameter_mm,
            max_piston_stroke_mm=max_piston_stroke_mm)

    def set_syringe_params_by_type(self, syringe_type='50 mL glass'):
        """
        Convenience method to set syringe parameters based on syringe type.

        Parameters
        ----------
        syringe_type : string
            Any of `25 mL glass` and `50 mL glass`.

        Notes
        -----
        This method simply looks up pre-defined syringe parameters (inner
        diameter and max. piston stroke), and passes these parameters to
        :func:~`pyqmix.QmixPump.set_syringe_params`.

        """
        syringes = {'25 mL glass': dict(inner_diameter_mm=23.03294,
                                        max_piston_stroke_mm=60),
                    '50 mL glass': dict(inner_diameter_mm=32.57350,
                                        max_piston_stroke=60)}

        if syringe_type not in syringes.keys():
            raise ValueError('Unknown syringe type.')
        else:
            syringe = syringes[syringe_type]

        self._call('LCP_SetSyringeParam',
                   self._handle[0],
                   syringe['inner_diameter_mm'],
                   syringe['max_piston_stroke_mm'])

        config.set_pump_syringe_params(
            self.index,
            inner_diameter_mm=syringe['inner_diameter_mm'],
            max_piston_stroke_mm=syringe['max_piston_stroke_mm'])

    def get_syringe_params(self):
        """
        Get the currently set syringe properties.

        Returns
        -------
        OrderedDict
            Returns a dictionary with the keys `inner_diameter_mm` and
            `max_piston_stroke_mm`.
        """
        self._call('LCP_GetSyringeParam', self._handle[0],
                   self._p_inner_diameter_mm, self._p_max_piston_stroke_mm)

        return OrderedDict(
            [('inner_diameter_mm', self._p_inner_diameter_mm[0]),
             ('max_piston_stroke_mm', self._p_max_piston_stroke_mm[0])])

    @property
    def syringe_params(self):
        """
        The currently set syringe properties.

        Returns
        -------
        OrderedDict
            Returns a dictionary with the keys `inner_diameter_mm` and
            `max_piston_stroke_mm`.
        """
        return self.get_syringe_params()

    @syringe_params.setter
    def syringe_params(self, params):
        self.set_syringe_params(**params)

    @property
    def max_flow_rate(self):
        """
        Maximum flow rate for the current dosing unit configuration.

        The maximum flow rate depends on the mechanical configuration of the
        dosing unit (gear) and on the syringe configuration. If larger syringes
        are used then larger flow rates are realizable.

        Returns
        -------
        float
            The maximum flow rate in configured SI unit

        """
        self._call('LCP_GetFlowRateMax', self._handle[0], self._flow_rate_max)
        return self._flow_rate_max[0]

    def aspirate(self, volume, flow_rate, blocking_wait=False):
        """
        Aspirate a certain volume with the specified flow rate.

        Parameters
        ----------
        volume : float
            The volume to aspirate in physical units.

        flow_rate : float
            The flow rate to use to aspirate the volume, negative flow rates are
            invalid.

        blocking_wait : bool
            Whether to block until done.

        Notes
        -----
        This method switches the valve to aspiration position
        before the actual aspiration begins.

        """
        self.valve.switch_position(self.valve.aspirate_pos)
        self._call('LCP_Aspirate', self._handle[0], volume, flow_rate)
        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)

    def dispense(self, volume, flow_rate, blocking_wait=False,
                 switch_valve_when_finished=False):
        """
        Dispense a certain volume with a certain flow rate.

        It also switches the valve in position 0 (green led off).

        Parameters
        ----------
        volume : float
            The volume to dispense in physical units.

        flow_rate : float
            The flow rate to use to dispense the volume, negative flow rates are
            invalid.

        blocking_wait : bool
            Whether to block until done.

        switch_valve_when_finished : bool
            If set to ``True``, it switches valve to postion 1 when dispense is
            finished. It only has effect if ``blocking_wait = True``.

        """
        self.valve.switch_position(self.valve.dispense_pos)
        self._call('LCP_Dispense', self._handle[0], volume, flow_rate)
        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)

            if switch_valve_when_finished:
                self.valve.switch_position(self.valve.aspirate_pos)

    def set_fill_level(self, level, flow_rate, blocking_wait=False):
        """
        Pumps fluid with the given flow rate until the requested fill level is
        reached.

        Depending on the requested fill level given in ``level`` parameter this
        function may cause aspiration or dispension of fluid. If it aspirates it
        switches the valve in position 1. 0 if it dispenses.

        Parameters
        ----------
        level : float
            The requested fill level. A level of 0 indicates a completely empty
            syringe.

        flow_rate : float
            The flow rate to use for pumping.

        blocking_wait : bool
            Whether to block until done.

        """
        if level < self.get_fill_level():
            self.valve.switch_position(self.valve.dispense_pos)
        else:
            self.valve.switch_position(self.valve.aspirate_pos)
        self._call('LCP_SetFillLevel', self._handle[0], level, flow_rate)

        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)

    def generate_flow(self, flow_rate, blocking_wait=False):
        """
        Generate a continuous flow.

        If it aspirates it switches the valve in position 1. 0 if it dispenses.

        Parameters
        ----------
        flow_rate : float
            A positive flow rate indicates dispensing and a negative flow rate
            indicates aspiration.

        blocking_wait : bool
            Whether to block until done.

        """
        if flow_rate > 0:
            self.valve.switch_position(self.valve.dispense_pos)
        else:
            self.valve.switch_position(self.valve.aspirate_pos)
        self._call('LCP_GenerateFlow', self._handle[0], flow_rate)
        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)

    def stop(self):
        """
        Immediately stop pumping.

        """
        self._call('LCP_StopPumping', self._handle[0])

    def stop_all_pumps(self):
        """
        Immediately stop all pumps.

        """
        self._call('LCP_StopAllPumps')

    @property
    def dosed_volume(self):
        """
        Get the already dosed volume.

        Returns
        -------
        float
            The already dosed volume

        """
        self._call('LCP_GetDosedVolume', self._handle[0], self._p_dosed_volume)
        return self._p_dosed_volume[0]

    def get_fill_level(self):
        """
        Returns the current fill level of the pump.

        Returns
        -------
        float
            The current fill level of the syringe

        """
        self._call('LCP_GetFillLevel', self._handle[0], self._p_fill_level)
        return self._p_fill_level[0]

    @property
    def fill_level(self):
        """
        Returns the current fill level of the pump.

        Notes
        -----
        This is identical to a call to :func:~`pyqmix.QmixPump.get_fill_level`.

        """
        return self.get_fill_level()

    @property
    def current_flow_rate(self):
        """
        Read the current flow rate.

        This does not assess the actual current flow rate. Instead, this method
        simply returns the cached (desired) flow rate value.

        Returns
        -------
        float
            The current flow rate demand value

        """
        self._call('LCP_GetFlowIs', self._handle[0], self._p_flow_rate)
        return self._p_flow_rate[0]

    @property
    def is_pumping(self):
        """
        Check if device is currently stopped or dosing.

        Returns
        -------
        bool
            `True` if pumping, `False` otherwise.
        """
        r = self._call('LCP_IsPumping', self._handle[0])
        return bool(r)

    @property
    def has_valve(self):
        """
        Check if the pump has a valve assigned.

        Returns
        -------
        bool
            `True` if a valve is present, `False` otherwise.

        """
        r = self._call('LCP_HasValve', self._handle[0])
        return bool(r)

    @property
    def valve_handle(self):
        """
        Returns the valve handle of the pump valve.

        Returns
        -------
        int
           Handle to valve device, or 0 if no valve is associated

        """
        self._call('LCP_GetValveHandle', self._handle[0], self._valve_handle)
        return self._valve_handle[0]

    def add_external_valve(self, valve, name):
        self.ext_valves[name] = valve

    def remove_external_valve(self, name):
        del self.ext_valves[name]

    @property
    def drive_pos_counter(self):
        """
        Current drive position counter of the pump.

        The position counter gets reset to zero when the pump system is powered
        off. To avoid having to recalibrate the system (i.e., doing a reference
        move, which requires removal of the syringes), this function may be
        used to save the current drive position counter to the configuration
        file, from where it can be safely restored once the system is powered
        on again.

        Returns
        -------
        int
            The current value of the drive position counter.

        """
        self._call('LCP_GetDrivePosCnt', self._handle[0],
                   self._p_drive_pos_counter)
        return self._p_drive_pos_counter[0]

    @drive_pos_counter.setter
    def drive_pos_counter(self, value):
        value = int(value)
        self._call('LCP_RestoreDrivePosCnt', self._handle[0], value)

    def save_drive_pos_counter(self):
        """
        Save the current drive position counter to the configuration file.

        """
        config.set_pump_drive_pos_counter(self.index, self.drive_pos_counter)


def init_pump(params):
    """Convenience function to initialize and calibrate a pump.

    Parameters
    ----------
    params : dict
        A dictionary with the following keys: `index`, `flow`, `volume`,
        `syringe`.

    Returns
    -------
    Readily initialized and calibrated class:~`pyqmix.QmixPump` instance.

    TODO: Improve documentation.

    """
    pump = QmixPump(index=params['index'])
    pump.set_flow_unit(**params['flow'])
    pump.set_volume_unit(**params['volume'])
    pump.set_syringe_params(**params['syringe'])
    pump.calibrate(blocking_wait=False)

    return pump


def fill_syringes(pumps, volume=None, flow_rate=1):
    """
    Fill syringes.

    Parameters:
    -----------
    pumps : list of class:~`pyqmix.QmixPump` instances

    """
    flow_rate = abs(flow_rate)

    if volume is None:
        flow_rate *= -1
        [p.generate_flow(flow_rate=flow_rate) for p in pumps]
    else:
        [p.aspirate(volume=volume, flow_rate=flow_rate) for p in pumps]

    while any([p.is_pumping for p in pumps]):
        time.sleep(0.0005)


def empty_syringes(pumps, volume=None, flow_rate=1):
    """
    Empty syringes.

    Parameters:
    -----------
    pumps : list of class:~`pyqmix.QmixPump` instances

    """
    flow_rate = abs(flow_rate)

    if volume is None:
        [p.generate_flow(flow_rate=flow_rate) for p in pumps]
    else:
        [p.dispense(volume=volume, flow_rate=flow_rate) for p in pumps]

    while any([p.is_pumping for p in pumps]):
        time.sleep(0.0005)
