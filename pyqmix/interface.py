#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from cffi import FFI
import time
import sys

if sys.version_info[0] < 3:
    # Python 2 compatibility; requires `future` package.
    from builtins import bytes

from .headers import (BUS_HEADER, PUMP_HEADER, VALVE_HEADER, DIGITAL_IO_HEADER,
                      ERROR_HEADER)


DLL_DIR = None


def CHK(return_code, *args):
    """
    Check if the return value of the invoked function returned an error.

    The Qmix DLL makes this pretty easy: All errors are indicated by
    negative return values.

    Parameters
    ----------
    return_code : int
        The code returned from a Qmix DLL function.
    args
        All arguments passed to the function ``funcname``.

    Returns
    -------
    return_code : int
        If no error occurred, the originally passed return value is
        returned.

    Raises
    ------
    RuntimeError
        If the DLL function returned an error code.

    """
    if return_code >= 0:
        return return_code
    else:  
        e = _QmixError(return_code)
        error_string = e.error_string
        msg = (error_string + ", Error number: " + str(e.error_number) +
               ", Error code: " + str(e.error_code))
        raise RuntimeError(msg)


class QmixBus(object):
    """
    It establishes the communication between the bus and the devices.
    
    First class that has to be initialized.

    Parameters
    ----------
    config_dir : str
        Absolute path to the folder that contains the device configuration files
        (XML config files).
        
    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.
        
    """     
    def __init__(self, config_dir, dll_dir):
        global DLL_DIR
        DLL_DIR = dll_dir

        self.dll_dir = dll_dir
        self.dll_file = os.path.join(self.dll_dir, 'labbCAN_Bus_API.dll')
        self.config_dir = config_dir        
        self._ffi = FFI()
        self._ffi.cdef(BUS_HEADER)        
        self._dll = self._ffi.dlopen(self.dll_file)
        self.is_open = False
        self.is_started = False

    def __del__(self):
        self.stop()
        self.close()
        
    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r
                  
    def open(self):
        """
        Initialize labbCAN bus.
        
        Initializes resources for a labbCAN bus instance, opens the bus and
        scans for connected devices.

        """        
        self._call('LCB_Open', bytes(self.config_dir, 'utf8'))
        time.sleep(1)
        self.is_open = True
    
    def close(self):
        """
        Close labbCAN bus.
        
        """
        self._call('LCB_Close')
        self.is_open = False
    
    def start(self):
        """
        Start bus network communication.
        
        Sets all connected devices operational and enables them.
        Connected devices can be accessed only after this method has been
        invoked.

        """         
        self._call('LCB_Start')
        time.sleep(1)
        self.is_started = True
    
    def stop(self):
        """
        Stop bus network communication.
        
        Stops network communication and closes the labbCAN device.
        The method should be called before calling
        :func:`qmix.QmixBus.close``.

        """         
        self._call('LCB_Stop')
        self.is_started = False


class QmixPump(object):
    """
    Qmix pump interface.

    Parameters
    ----------        
    index : int, or None
        Index of the pump to access. It is related with the config files.
        First pump has ``index=0``, second has ``index=1`` and so on.
        Takes precedence over the `name` parameter.

    name : str
        The name of the pump to initialize. Will be ignored if `index` is
        not `None`.
        
    """
    def __init__(self, index=None, name='', external_valves=None):
        if index is None and name == '':
            raise ValueError('Please specify a valid pump index or name')
        else:
            self.index = index
            self.name = name

        self.dll_file = os.path.join(DLL_DIR, 'labbCAN_Pump_API.dll')
        
        self._ffi = FFI()
        self._ffi.cdef(PUMP_HEADER)                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self._handle = self._ffi.new('dev_hdl *', 0)

        if self.index is not None:
            self._call('LCP_GetPumpHandle', self.index, self._handle)
        else:
            self._call('LCP_LookupPumpByName',
                       bytes(self.name, 'utf8'),
                       self._handle)

        self._flow_rate_max = self._ffi.new('double *')       
        self._p_fill_level = self._ffi.new('double *')
        self._p_dosed_volume = self._ffi.new('double *')
        self._p_flow_rate = self._ffi.new('double *')
        
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
            
        self.name = name

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r 
           
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
        return self._call('LCP_Enable', self._handle[0])
    
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
        return self._call('LCP_ClearFault', self._handle[0])        

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

    def calibrate(self, blocking_wait=True):
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

    def set_volume_unit(self, prefix=None, unit=None):
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
        
    def set_flow_unit(self, prefix=None, volume_unit=None, time_unit=None):
        """
        Set the flow unit for a certain pump.
        
        The flow unit defines the unit to be used for all flow values passed to 
        API functions or retrieved from API functions.

        Parameters
        ----------
        prefix : str
            The prefix of the SIunit:
            ``centi``, ``deci``, ``mircro``, ``milli``, ``unit``.
            
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
    
    # TODO: find reasonable default parameters
    def set_syringe_param(self, inner_diameter_mm=23.03, max_piston_stroke_mm=60):
        """
        Set syringe properties.
        
        If you change the syringe in one device, you need to setup the new
        syringe parameters to get proper conversion of flow rate und volume
        units.

        Parameters
        ----------
        inner_diameter_mm : float
            Inner diameter of the syringe tube in millimetres. Default is
            23.03 (mm) that indicates a 25 ml syringe. For the 50 ml syringe
            use 32.5 (mm).
            
        max_piston_stroke_mm : float
            The maximum piston stroke defines the maximum position the piston
            can be moved to before it slips out of the syringe tube. The maximum
            piston stroke limits the maximum travel range of the syringe pump
            pusher.

        """        
        self._call('LCP_SetSyringeParam', self._handle[0], inner_diameter_mm,
                   max_piston_stroke_mm)

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
        This method switches the valve in position 1 (green led activated)
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
            
        Returns
        -------

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
    
    #TODO: modify?
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

    @property
    def fill_level(self):
        """
        Returns the current fill level of the pump.

        Notes
        -----
        This is identical to a call to :func:~`pyqmix.QmixPump.get_fill_level`.
        """

        return self.get_fill_level()
    
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


class QmixValve(object):
    """
    Qmix valve interface.

    Parameters
    ----------
    index : int, or None
        Index of the valve to initialize. Takes precedence over the
        `name` and `handle` parameters.

    name : str
        The name of the valve to initialize. Will be ignored if `index` is
        not `None`. Takes precedence over the `handle` parameter.

    handle :  Qmix valve handle, or None
        A Qmix valve device handle, as returned by
        :func:~`pyqmix.QmixPump.valve_handle`.

    """
    def __init__(self, index=None, name='', handle=None):
        if index is None and name == '' and handle is None:
            raise ValueError('Please specify a valid valve index or name.')
        else:
            self.index = index
            self.name = name
            self.handle = handle

        self.dll_file = os.path.join(DLL_DIR, 'labbCAN_Valve_API.dll')
    
        self._ffi = FFI()
        self._ffi.cdef(VALVE_HEADER)                                          
        self._dll = self._ffi.dlopen(self.dll_file)

        if self.index is not None:
            self._handle = self._ffi.new('dev_hdl *', 0)
            self._call('LCV_GetValveHandle', self.index, self._handle)
        elif self.name != '':
            self._call('LCV_LookupValveByName',
                       bytes(self.name, 'utf8'),
                       self._handle)
        else:
            self._handle = handle
            
        self.aspirate_pos = 0
        self.dispense_pos = 1
        
        self.name = name

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r 

    @property
    def number_of_positions(self):
        """
        Return the number of valve positions.
        
        Each valve has a number of available valve positions. 
        A switching valve has two positions.
        
        Returns
        -------
        int                                
           >0 Number of valve positions

        """        
        return self._call('LCV_NumberOfValvePositions', self._handle[0])
    
    @property
    def current_position(self):
        """
        Return the current logical valve position.
        
        Each valve position is identified by a logical valve position identifier 
        from 0 to number of valve positions - 1. This function returns the
        logical valve position identifier for the current valve position.
        
        Returns
        -------
        int                                
           >=0 current valve position index. 

        """         
        return self._call('LCV_ActualValvePosition', self._handle[0])
    
    def switch_position(self, position=None):
        """
        Switch the valve to a certain logical valve position.

        Parameters
        ----------
        position : int, or None
            Switch the valve to the specified position.
            If `None` and a valve with two possible positions is connected,
            switch from the current position to the other one.

        """
        if position is None and self.number_of_positions != 2:
            msg = ('For valves with more than 2 positions, please specify the '
                   'desired target position.')
            raise ValueError(msg)

        if position is None:
            if self.current_position == 0:
                target_position = 1
            else:
                target_position = 0
        else:
            target_position = position

        self._call('LCV_SwitchValveToPosition', self._handle[0],
                   target_position)


class QmixExternalValve(QmixValve):
    """
    An external valve, controlled by Qmix I/O-B.

    Parameters
    ----------
    index : int, or None
        Index of the DIO channel to istantiate. Takes precedence over the
        `name` parameter.

    name : str
        The name of the DIO channel to initialize. Will be ignored if `index` is
        not `None`.

    """    
    def __init__(self, index=None, name=''):
        if index is None and name == '':
            raise ValueError('Please specify a valid DIO index or name')
        else:
            self.index = index
            self.name = name

        if self.index is not None:
            self._dio = QmixDigitalIO(index=self.index)
        else:
            self._dio = QmixDigitalIO(name=self.name)
        
        self.aspirate_pos = 0
        self.dispense_pos = 1

    def switch_position(self, position=None):
        """
        Switch the valve to a certain logical valve position.

        Parameters
        ----------
        position : int, or None
            Switch the valve to the specified position.
            If `None` and a valve with two possible positions is connected,
            switch from the current position to the other one.

        """
        if position is None:
            if self.current_position == 0:
                target_position = 1
            else:
                target_position = 0
        else:
            target_position = position

        self._dio.write(target_position)

    @property
    def current_position(self):        
        r = self._dio.is_output_on

        if r:
            return 1
        else:
            return 0

    @property
    def number_of_positions(self):
        return 2


class QmixDigitalIO(object):
    """
    Qmix IO-B diglital I/O channel.

    Parameters
    ----------
    index : int
        Index of the DIO channel. It is related with the config files.
        First channel has ``index=0``, second has ``index=1`` and so on.
        Takes precedence over the `name` parameter.

    name : str
        The name of the DIO channel to initialize. Will be ignored if `index` is
        not `None`.

    """     
    def __init__(self, index=None, name=''):
        if index is None and name == '':
            raise ValueError('Please specify a valid DIO index or name.')
        else:
            self.index = index
            self.name = name

        self.dll_file = os.path.join(DLL_DIR, 'labbCAN_DigIO_API.dll')
        self._ffi = FFI()
        self._ffi.cdef(DIGITAL_IO_HEADER)
                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self._handle = self._ffi.new('dev_hdl *', 0)

        if self.index is not None:
            self._call('LCDIO_GetOutChanHandle', self.index, self._handle)
        else:
            self._call('LCDIO_LookupOutChanByName',
                       bytes(self.name, 'utf8'),
                       self._handle)

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r  
        
    @property
    def is_output_on(self):
        """
        Current state of a digital output channel.
        
        Returns
        -------
        int                                
           1	Channel is ON
           0	Channel is OFF 

        """          
        r = self._call('LCDIO_IsOutputOn', self._handle[0])
        return bool(r)
    
    def write(self, state):
        """
        Swicth digital output channel on/off.

        Parameters
        ---------- 
        state : int
            State to set 0 = switch off, 1 = switch on.

        """         
        self._call('LCDIO_WriteOn', self._handle[0], state)
 

class _QmixError(object):
    def __init__(self, error_number):
        self.dll_file = os.path.join(DLL_DIR, 'usl.dll')
        self._ffi = FFI()
        self._ffi.cdef(ERROR_HEADER)
                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self.error_number = error_number
        self._error_code = self._ffi.new('TErrCode *')
    
    @property
    def error_code(self):
        self._error_code = hex(abs(self.error_number))
        return self._error_code
    
    @property
    def error_string(self):
        e = self.error_code
        s = self._dll.ErrorToString(int(e, 16))
        return self._ffi.string(s).decode('utf8')
        
    
if __name__ == '__main__':
    import os.path as op

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
    
    pump_0.set_syringe_param()
    pump_1.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    pump_2.set_syringe_param()
    pump_3.set_syringe_param()
    
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
