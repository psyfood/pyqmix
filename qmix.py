# -*- coding: utf-8 -*-
"""
Created on Thu May 18 10:58:59 2017

@author: alfine-l

"""
import os
from cffi import FFI
import time

def CHK(return_code, funcname, *args):
    """
    Check if the return value of the invoked function returned an error.

    The Qmix DLL makes this pretty easy: All errors are indicated by
    negative return values.

    Parameters
    ----------
    return_code : int
        The code returned from a Qmix DLL function.
    funcname : str
        The name of the invoked DLL function.
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
        msg = f'{error_string}, Error number: {e.error_number}, Error code {e.error_code}'
        raise RuntimeError(msg)

BUS_HEADER =  """
    typedef long long labb_hdl;    
    typedef long long dev_hdl;    
    long LCB_Open(const char* pDeviceConfigPath);    
    long LCB_Start();    
    long LCB_Stop();    
    long LCB_Close();
 """

class QmixBus(object):
    """
    It establishes the communication between the bus and the devices.
    
    First class that has to be initialized.

    Parameters
    ----------
    config_dir : str
        Absolute path to the folder that contains the device configuration files (XML config files).
        
    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.
        
    """     
    def __init__(self, config_dir=None, dll_dir=None):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_Bus_API.dll')

        if config_dir is None:
            self.config_dir = os.path.normpath('C:/Users/Public/Documents/QmixElements/Projects/test/Configurations/test_qmix2017')
        else:
            self.config_dir = config_dir
        
        self._ffi = FFI()
        self._ffi.cdef(BUS_HEADER)
        
        self._dll = self._ffi.dlopen(self.dll_file)
        self.is_open = False
        self.is_started = False

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r     
                  
    def open(self):
        """
        Initialize LabCanBus instance.
        
        Initializes resources for a LabCanBus instance, connects to LabCanBus and scans for connected devices.

        Parameters
        ----------

        Returns
        -------

        """        
        self._call('LCB_Open', bytes(self.config_dir,'utf8'))
        time.sleep(1)
        self.is_open = True
    
    def close(self):
        """
        Close LabCanBus instance.
        
        This call deletes all internal data structures and frees all allocated resources.

        Parameters
        ----------

        Returns
        -------

        """          
        self._call('LCB_Close')
        self.is_open = False
    
    def start(self):
        """
        Start network communication.
        
        This function sets all connected devices into state operational and enabled.
        After a call to this function it is possible to access the connected devices.

        Parameters
        ----------

        Returns
        -------

        """         
        self._call('LCB_Start')
        time.sleep(1)
        self.is_started = True
    
    def stop(self):
        """
        Stop network communication.
        
        This function stops network communication and closes the CAN device driver.
        The function should be called by application before ``QmixBus.close()``.

        Parameters
        ----------

        Returns
        -------

        """         
        self._call('LCB_Stop')
        self.is_started = False
            
    def __del__(self):
        self.stop()
        self.close()
        

PUMP_HEADER = """
                     #define LITRES 68 //!< LITRES
                     #define UNIT   0 //!< use base unit
                     #define DECI  -1 //!< DECI
                     #define CENTI -2 //!< CENTI
                     #define MILLI -3 //!< MILLI
                     #define MICRO -6 //!< MICRO
                     #define PER_SECOND    1 //!< PER_SECOND
                     #define PER_MINUTE   60 //!< PER_MINUTE
                     #define PER_HOUR   3600 //!< PER_HOUR
                        
                     typedef long long dev_hdl;
                     long LCP_GetNoOfPumps();
                     long LCP_GetPumpHandle(unsigned char Index, dev_hdl* PumpHandle);
                     long LCP_LookupPumpByName(const char *pPumpName, dev_hdl* PumpHandle);
                     long LCP_IsEnabled(dev_hdl hPump);
                     long LCP_Enable(dev_hdl hPump);
                     long LCP_SyringePumpCalibrate(dev_hdl 	hPump);
                     long LCP_IsCalibrationFinished(dev_hdl hPump);
                     long LCP_IsInFaultState(dev_hdl hPump);  
                     long LCP_ClearFault(dev_hdl hPump);
                     long LCP_SetVolumeUnit(dev_hdl hPump,
                                                  int    Prefix,
                                                  int     VolumeUnit);
                     long LCP_SetFlowUnit(dev_hdl hPump,
                                                int    Prefix,
                                                int     VolumeUnit,
                                                int     TimeUnit);
                     long LCP_SetSyringeParam(dev_hdl hPump,
                                                    double  InnerDiameter_mm,
                                                    double  MaxPistonStroke_mm);
                     long LCP_Aspirate(dev_hdl hPump, double Volume, double Flow);
                     long LCP_Dispense(dev_hdl hPump, double Volume, double Flow);
                     long LCP_PumpVolume(dev_hdl hPump, double Volume, double Flow);
                     long LCP_SetFillLevel(dev_hdl hPump,
        	                                     double  Level,
        	                                     double  Flow);
                     long LCP_GenerateFlow(dev_hdl hPump, double FlowRate);
                     long LCP_GetDosedVolume(dev_hdl hPump, double *pDosedVolume);
                     long LCP_GetFillLevel(dev_hdl hPump, double* pFillLevel);
                     long LCP_GetFlowIs(dev_hdl hPump, double *pFlowRateIs);
                     long LCP_IsPumping(dev_hdl hPump);
                     long LCP_GetFlowRateMax(dev_hdl hPump, double* FlowRateMax);
                     long LCP_StopPumping(dev_hdl hPump);
                     long LCP_StopAllPumps();
                     long LCP_GetValveHandle(dev_hdl hPump, dev_hdl* ValveHandle);
                     long LCP_HasValve(dev_hdl hPump);
                     long LCP_GetDrivePosCnt(dev_hdl hPump, long *pPosCntValue);
                     long LCP_RestoreDrivePosCnt(dev_hdl hPump, long PosCntValue);
                     """

class QmixPump(object):
    """
    Istantiate a pump object.

    Parameters
    ----------
    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.
        
    index : int
        Index of the pump to istantiate. It is related with the config files.
        First pump has ``index = 0``, second has ``index = 1`` and so on.
        
    """
    def __init__(self, dll_dir=None, index=0):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_Pump_API.dll')
        
        self._ffi = FFI()
        self._ffi.cdef(PUMP_HEADER)
                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self._handle = self._ffi.new('dev_hdl *', 0)
        self._call('LCP_GetPumpHandle', index, self._handle)        

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
            1	- Pump drive is enabled, pumping is possible
            0	- Pump drive is disabled - pump head is free running

        """        
        return self._call('LCP_IsEnabled', self._handle[0])
           
    def enable(self):
        """
        Set axis into enabled state.
        
        If the function ``QmixPump.is_enabled()`` indicates that the device is disabled then call this function.

        Parameters
        ----------

        Returns
        -------

        """            
        return self._call('LCP_Enable',self._handle[0])
    
    @property    
    def is_in_fault_state(self):
        """
        Check if pump is in a fault state.

        If the device is in fault state then it is necessary to call ``QmixPump.clear_fault_state()``
        to clear the fault state and then ``QmixPump.enable()`` to enable the pump drive.
        
        Returns
        -------
        int                 
            1	- Pump is in fault state
            0	- Pump is not in fault state

        """         
        return self._call('LCP_IsInFaultState', self._handle[0])    

    def clear_fault_state(self):
        """
        Clear fault condition.
        
        This is some kind of error acknowledge that clears the last fault and sets the 
        device in an error free state. If the function ``QmixPump.is_in_fault_state()`` 
        indicates that device is in fault state, then this function may clear the fault.
        If the device is still in fault state after this function was called then a serious failure occurred.

        Parameters
        ----------

        Returns
        -------

        """         
        return self._call('LCP_ClearFault', self._handle[0])        

    @property 
    def is_calibration_finished(self):
        """
        Checks if calibration is finished or performed.
        
        Returns
        -------
        int                                
            0	- Device is calibrating
            1	- Device calibration has finished/was perfomed

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
            Whether to block until done.

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
            >=	0 Number of detected pump devices

        """          
        return self._call('LCP_GetNoOfPumps')

    def set_volume_unit(self, prefix=None, unit=None):
        """
        This function sets the default volume unit.
        
        All parameters of subsequent dosing function calls are given in this new unit.

        Parameters
        ----------
        prefix : str
            The prefix of the SIunit: ``centi``, ``deci``, ``mircro``, ``milli``, ``unit``.
            
        unit : str
            The volume unit identifier: ``litres``.

        Returns
        -------

        """         
        self._call('LCP_SetVolumeUnit', self._handle[0],
                                    getattr(self._dll, prefix.upper()),
                                    getattr(self._dll, unit.upper()))
        
    def set_flow_unit(self, prefix=None, volume_unit=None, time_unit=None):
        """
        Sets the flow unit for a certain pump.
        
        The flow unit defines the unit to be used for all flow values passed to 
        API functions or retrieved from API functions.

        Parameters
        ----------
        prefix : str
            The prefix of the SIunit: ``centi``, ``deci``, ``mircro``, ``milli``, ``unit``.
            
        volume_unit : str
            The volume unit identifier: ``litres``.
            
        time_unit : str
            The time unit (denominator) of the velocity unit: ``per_hour``, ``per_minute``,
            ``per_second``.

        Returns
        -------

        """         
        self._call('LCP_SetFlowUnit', self._handle[0],
                                  getattr(self._dll, prefix.upper()),
                                  getattr(self._dll, volume_unit.upper()),
                                  getattr(self._dll, time_unit.upper()))
    
    # TODO: find reasonable default parameters
    def set_syringe_param(self, inner_diameter_mm=23, max_piston_stroke_mm=60):
        """
        Set syringe parameters.
        
        If you change the syringe in one device, you need to setup the new syringe 
        parameters to get proper conversion of flow rate und volume units.

        Parameters
        ----------
        inner_diameter_mm : float
            Inner diameter of the syringe tube in millimetres.
            
        max_piston_stroke_mm : float
            The maximum piston stroke defines the maximum position the piston can 
            be moved to before it slips out of the syringe tube. The maximum piston
            stroke limits the maximum travel range of the syringe pump pusher.
            
        Returns
        -------

        """        
        self._call('LCP_SetSyringeParam', self._handle[0], inner_diameter_mm,
                                      max_piston_stroke_mm)
    @property    
    def max_flow_rate(self):
        """
        Get maximum flow rate that is realizable with current dosing unit configuration.
        
        The maximum flow rate depends on the mechanical configuration of the dosing 
        unit (gear) and on the syringe configuration. If larger syringes are used 
        then larger flow rates are realizable.
        
        Returns
        -------
        float                                
            The maximum flow rate in configured SI unit

        """         
        self._call('LCP_GetFlowRateMax', self._handle[0], self._flow_rate_max)
        return self._flow_rate_max[0]
         
    def aspirate(self, volume, flow_rate, blocking_wait=False):
        """
        Aspirate a certain volume with a certain flow rate.
        
        It also switches the valve in position 1 (green led activated).

        Parameters
        ----------
        volume : float
            The volume to aspirate in physical units.
            
        flow_rate : float
            The flow rate to use to aspirate the volume, negative flow rates are invalid.
            
        blocking_wait : bool
            Whether to block until done.        
            
        Returns
        -------

        """          
        self.valve.switch_position(1)
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
            The flow rate to use to dispense the volume, negative flow rates are invalid.
            
        blocking_wait : bool
            Whether to block until done.
            
        switch_valve_when_finished : bool
            If set to ``True``, it switches valve to postion 1 when dispense is finished.
            
        Returns
        -------

        """         
        self.valve.switch_position(0)
        self._call('LCP_Dispense', self._handle[0], volume, flow_rate)        
        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)
            if switch_valve_when_finished:
                self.valve.switch_position(1)
       
#    def pump_volume(self, volume, flow_rate): # NOT WORKING WITH NEGATIVE VALUES, TO FIX
#        self._dll.LCP_PumpVolume(self._handle[0], volume, flow_rate)
        
    def set_fill_level(self, level, flow_rate, blocking_wait=False):
        """
        Pumps fluid with the given flow rate until the requested fill level is reached.
        
        Depending on the requested fill level given in ``level`` parameter this function
        may cause aspiration or dispension of fluid. If it aspirates it switches the
        valve in position 1. 0 if it dispenses.

        Parameters
        ----------
        level : float
            The requested fill level. A level of 0 indicates a completely empty syringe.
            
        flow_rate : float
            The flow rate to use for pumping.
            
        blocking_wait : bool
            Whether to block until done.
                        
        Returns
        -------

        """        
        if level < self.get_fill_level():
            self.valve.switch_position(0)
        else:
            self.valve.switch_position(1)         
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
            A positive flow rate indicates dispensing and a negative flow rate indicates aspiration.
            
        blocking_wait : bool
            Whether to block until done.
                        
        Returns
        -------

        """        
        if flow_rate > 0:
            self.valve.switch_position(0)
        else:
            self.valve.switch_position(1)            
        self._call('LCP_GenerateFlow', self._handle[0], flow_rate)
        if blocking_wait:
            while self.is_pumping:
                time.sleep(0.0005)
        
    def stop(self):
        """
        Immediately stop pumping.

        Parameters
        ----------            
                        
        Returns
        -------

        """          
        self._call('LCP_StopPumping', self._handle[0])
    
    #TODO: modify?    
    def stop_all_pumps(self): # should be callable without a pump object
        """
        Immediately stop pumping.

        Parameters
        ----------            
                        
        Returns
        -------

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

        Parameters
        ----------            
                        
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
        
        This does not read the real flow rate instead this function returns simply
        the cached flow rate demand value.
        
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
        int                                
            1	- Device is pumping
            0	- Device is stopped

        """         
        r = self._call('LCP_IsPumping', self._handle[0]) 
        return bool(r)
    
    @property
    def has_valve(self):
        """
        Returns 1 if this pump has an valve assigned.
        
        Returns
        -------
        int                                
            0	- No valve assigned to this pump
            1	- Valve assigned to this pump

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
           Handle to valve device or 0 if no valve is associated 

        """          
        self._call('LCP_GetValveHandle', self._handle[0], self._valve_handle)
        return self._valve_handle[0]


VALVE_HEADER =  """
    typedef long long dev_hdl;
    long LCV_GetNoOfValves();
    long LCV_LookupValveByName(const char *pValveName,
	   dev_hdl* ValveHandle);
    long LCV_GetValveHandle(unsigned char Index,
	   dev_hdl* ValveHandle);
    long LCV_NumberOfValvePositions(dev_hdl hValve);
    long LCV_ActualValvePosition(dev_hdl hValve);
    long LCV_SwitchValveToPosition(dev_hdl hValve,
	                                              int     LogicalValvePosition);
    
 """

class QmixValve(object):
    """
    Istantiate a valve object.

    Parameters
    ----------
    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.
        
    index : int
        Index of the valve to istantiate. If a ``handle`` is passed this parameter
        it is not used.
        
    handle :  dev_hdl
        Used when initializing a ``QmixPump`` object. It is not used if a ``index`` 
        parameter is passed.
        
    """    
    def __init__(self, dll_dir=None, index=0, handle=None):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_Valve_API.dll')
    
        self._ffi = FFI()
        self._ffi.cdef(VALVE_HEADER)
                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        if handle is None:
            self.index = index
            self._handle = self._ffi.new('dev_hdl *', 0)
            self._call('LCV_GetValveHandle', self.index, self._handle)
        else:
            self.index = None
            self._handle = handle

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r 

    @property
    def number_of_positions(self):
        """
        Returns the number of valve positions.
        
        Each valve has a number of available valve positions. 
        A switching valve has two positions.
        
        Returns
        -------
        int                                
           >0	Number of valve positions 

        """        
        return self._call('LCV_NumberOfValvePositions', self._handle[0])
    
    @property
    def current_position(self):
        """
        Returns the current logical valve position.
        
        Each valve position is identified by a logical valve position identifier 
        from 0 to number of valve positions - 1. This function returns the logical valve
        position identifier for the current valve position.
        
        Returns
        -------
        int                                
           >=0 current valve position index. 

        """         
        return self._call('LCV_ActualValvePosition', self._handle[0])
    
    def switch_position(self, position=0):
        """
        Switches the valve to a certain logical valve position.

        Parameters
        ---------- 
        position : int
            Logical valve target position index.
                        
        Returns
        -------

        """        
        self._call('LCV_SwitchValveToPosition', self._handle[0], position)
    
DIGITAL_IO_HEADER =  """
    typedef long long dev_hdl;
    long LCDIO_LookupOutChanByName(const char* pChannelName, dev_hdl *   pOutChanHdl);
    long LCDIO_LookupInChanByName(const char* pChannelName, dev_hdl*    pInChanHdl);
    long LCDIO_WriteOn(dev_hdl OutChanHdl, int On);
    long LCDIO_IsOutputOn(dev_hdl OutChanHdl);
    long LCDIO_IsInputOn(dev_hdl InChanHdl);
    long LCDIO_GetChanName(dev_hdl  hChan, char    *pNameStringBuf,
                                            int      StringBufSize);
    long LCDIO_LookupIoDeviceByName(const char *pName,
                                                     dev_hdl    *pIoDeviceHdl);
    
 """

class QmixDigitalIO(object):
    """
    Istantiate a valve object.

    Parameters
    ----------
    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.
        
    index : int
        Index of the digital channel to istantiate. It is related with the config files.
        First channel has ``index = 0``, second has ``index = 1`` and so on.
                
    """     
    def __init__(self, dll_dir=None, index=0):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_DigIO_API.dll')
        self._ffi = FFI()
        self._ffi.cdef(DIGITAL_IO_HEADER)
                                          
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self._handle = self._ffi.new('dev_hdl *', 0)
        
        self._ch_name="QmixIO_B_1_DO"
        self._channel = self._ch_name + str(index) 
        self._call('LCDIO_LookupOutChanByName', bytes(self._channel,'utf8'), self._handle)

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r  
        
    @property
    def is_output_on(self):
        """
        Return the state of a digital output channel.
        
        Returns
        -------
        int                                
           1	Channel is ON
           0	Channel is OFF 

        """          
        r = self._call('LCDIO_IsOutputOn', self._handle[0])
        return bool(r)
    
    def write_on(self, state):
        """
        Swicth digital output channel on/off.

        Parameters
        ---------- 
        state : int
            State to set 0 = switch off, 1 = switch on.
                        
        Returns
        -------

        """         
        self._call('LCDIO_WriteOn', self._handle[0], state)
 
ERROR_HEADER = """
    #define USL_DECL ... 
    typedef int32_t TErrCode;
    const char* ErrorToString(TErrCode ErrCode);
    TErrCode errnoToErrCode(int errnum);
    
    #define ERR_NOERR           0x0000     ///< No error
    #define ERR_PERM            0x0001     ///< Not permitted
    #define ERR_NOENT           0x0002     ///< No such entity
    #define ERR_SRCH            0x0003     ///< No such process
    #define ERR_INTR            0x0004     ///< Operation interrupted 
    #define ERR_IO              0x0005     ///< I/O error 
    #define ERR_2BIG            0x0006     ///< Argument list too long
    #define ERR_NOEXEC          0x0007     ///< Executable format error
    #define ERR_CHILD           0x0008     ///< No child process
    #define ERR_BADF            0x0009     ///< Bad file handle
    #define ERR_MLINK           0x000A     ///< Too many links
    #define ERR_AGAIN           0x000B     ///< Try again later
    #define ERR_WOULDBLOCK      0x000B ///< \see ERR_AGAIN 
    #define ERR_NOMEM           0x000C    ///< Out of memory 
    #define ERR_ACCES			0x000D	  ///< Permission denied
    #define ERR_FAULT			0x000E	  ///< Bad address
    #define ERR_NOLCK           0x000F    ///< No lock available
    #define ERR_BUSY            0x0010    ///< Resource busy
    #define ERR_XDEV            0x0012    ///< Cross-device link
    #define ERR_NODEV           0x0013    ///< No such device
    #define ERR_NOTDIR          0x0014    ///< Not a directory
    #define ERR_ISDIR           0x0015    ///< Is a directory
    #define ERR_INVAL           0x0016    ///< Invalid argument
    #define ERR_NFILE           0x0017    ///< Too many open files in system
    #define ERR_MFILE           0x0018    ///< Too many open files
    #define ERR_NOTTY			0x0019	  ///< Not a typewriter
    #define ERR_FBIG            0x001B    ///< File too large
    #define ERR_NOSPC           0x001C    ///< No space left on device
    #define ERR_SPIPE           0x001D    ///< Illegal seek
    #define ERR_ROFS            0x001E    ///< Read-only file system
    #define ERR_ILSEQ           0x001F    ///< Illegal byte sequence
    #define ERR_PIPE2			0x0020	  ///< Broken pipe
    #define ERR_DOM             0x0021    ///< Argument to math function outside valid domain
    #define ERR_RANGE           0x0022    ///< Math result cannot be represented
    #define ERR_DEADLK          0x0023    ///< Resource deadlock would occur 
    #define ERR_DEADLOCK        0x0023 ///< \see ERR_DEADLK */
    #define ERR_CANCELED        0x0024    ///< Operation canceled
    #define ERR_OVERFLOW        0x0025    ///< Value too large
    #define ERR_NOSYS           0x0026    ///< Function not implemented
    #define ERR_OWNERDEAD       0x0027    ///< Owner dead
    #define ERR_LOOP			0x0028    ///< Too many symbolic links encountered
    #define ERR_NAMETOOLONG     0x003C    ///< File name too long     
    #define ERR_NOTEMPTY        0x0042    ///< Directory not empty 
    #define ERR_NOTSOCK			0x0058	  ///< Socket operation on non-socket
    #define ERR_DESTADDRREQ		0x0059	  ///< Destination address required
    #define ERR_NOPROTOOPT		0x005C	  ///< Protocol not available
    #define ERR_PROTONOSUPPORT	0X005D	  ///< Protocol not supported
    #define ERR_NOTSUP          0x005F    ///< Not supported error 
    #define ERR_AFNOSUPPORT		0x0061	  ///< Address family not supported by protocol
    #define ERR_ADDRINUSE		0x0062	  ///< Address already in use
    #define ERR_ADDRNOTAVAIL	0x0063	  ///< Cannot assign requested address
    #define ERR_NOBUFS			0X0069	  ///< No buffer space available
    #define ERR_EDQUOT			0x007A	  ///< Quota exceeded
    #define ERR_NOTBLK          0x007B    ///< Block device required
    #define ERR_TXTBSY          0x007C    ///< Text file busy
    #define ERR_NOMSG           0x007D    ///< No message of desired type
    #define ERR_IDRM            0x007E    ///< Identifier removed
    #define ERR_CHRNG           0x007F    ///< Channel number out of range
    
    #define ERR_L2NSYNC         0x0080    ///<  Level 2 not synchronized
    #define ERR_L3HLT           0x0081    ///<  Level 3 halted
    #define ERR_L3RST           0x0082    ///<  Level 3 reset
    #define ERR_LNRNG           0x0083    ///<  Link number out of range
    #define ERR_UNATCH          0x0084    ///<  Protocol driver not attached
    #define ERR_NOCSI           0x0085    ///<  No CSI structure available
    #define ERR_L2HLT           0x0086    ///<  Level 2 halted
    #define ERR_BADE            0x0087    ///<  Invalid exchange
    #define ERR_BADR            0x0088    ///<  Invalid request descriptor
    #define ERR_XFULL           0x0089    ///<  Exchange full
    #define ERR_NOANO           0x008A    ///<  No anode
    #define ERR_BADRQC          0x008B    ///<  Invalid request code
    #define ERR_BADSLT          0x008C    ///<  Invalid slot
    
    #define ERR_EOF             0x00C8    ///< End of file reached
    #define ERR_NOSUPP          0x00C9    ///< Operation not supported 
    #define ERR_DEVNOSUPP       0x00CA    ///< Device does not support this operation
    #define ERR_UNKNOWN         0x00CB    ///< Unknown error or unknown error code
    #define ERR_NET_NXIO            0x012C   ///< Device not configured
    #define ERR_NET_ACCES           0x012D   ///< Permission denied
    #define ERR_NET_EXIST           0x012E   ///< File exists
    #define ERR_NET_NOTTY           0x012F   ///< Inappropriate ioctl for device
    #define ERR_NET_PIPE            0x0130   ///< Broken pipe
    #define ERR_INPROGRESS      0x0136   ///< Operation now in progress
    #define ERR_ALREADY         0x0137   ///< Operation already in progress
    #define ERR_NET_NOTSOCK         0x0140   ///< Socket operation on non-socket
    #define ERR_NET_DESTADDRREQ     0x0141   ///< Destination address required
    #define ERR_NET_MSGSIZE         0x0142   ///< Message too long
    #define ERR_NET_PROTOTYPE       0x0143   ///< Protocol wrong type for socket
    #define ERR_NET_NOPROTOOPT      0x0144   ///< Protocol not available
    #define ERR_NET_PROTONOSUPPORT  0x0145   ///< Protocol not supported
    #define ERR_NET_SOCKTNOSUPPORT  0x0146   ///< Socket type not supported
    #define ERR_NET_OPNOTSUPP       0x0147   ///< Operation not supported
    #define ERR_NET_PFNOSUPPORT     0x0148   ///< Protocol family not supported
    #define ERR_NET_AFNOSUPPORT     0x0149   ///< Address family not supported by
                                          ///< protocol family 
    #define ERR_NET_ADDRINUSE       0x014A   ///< Address already in use
    #define ERR_NET_ADDRNOTAVAIL    0x014B   ///< Can't assign requested address
    #define ERR_NET_NETDOWN         0x015E  ///< Network is down
    #define ERR_NET_NETUNREACH      0x015F   ///< Network is unreachable
    #define ERR_NET_NETRESET        0x0160   ///< Network dropped connection on reset
    #define ERR_NET_CONNABORTED     0x0161   ///< Software caused connection abort
    #define ERR_NET_CONNRESET       0x0162   ///< Connection reset by peer
    #define ERR_NET_NOBUFS          0x0163   ///< No buffer space available
    #define ERR_NET_ISCONN          0x0164   ///< Socket is already connected
    #define ERR_NET_NOTCONN         0x0165   ///< Socket is not connected
    #define ERR_NET_SHUTDOWN        0x0166   ///< Can't send after socket shutdown
    #define ERR_NET_TOOMANYREFS     0x0167   ///< Too many references: can't splice
    #define ERR_NET_TIMEDOUT        0x0168   ///< Operation timed out
    #define ERR_NET_CONNREFUSED     0x0169   ///< Connection refused
    
    #define ERR_NET_HOSTDOWN        0x016C   ///< Host is down
    #define ERR_NET_HOSTUNREACH     0x016D   ///< No route to host
    #define ERR_ABORT           0x0200   ///< user aborted something
    #define ERR_PARAM_RANGE     0x0201   ///< value range of parameter exceeded
    #define ERR_ERROR           0x0202   ///< common unspecified error
    #define ERR_EXCEPTION       0x0203   ///< application has thrown an exception
    #define ERR_DEVCFG          0x0204   ///< invalid device configuration
    #define ERR_DEVSTATE        0x0205   ///< wrong device state for this operation
    #define ERR_LISTEMPTY       0x0206   ///< could not execute an operation because of an empty list
    #define ERR_NO_DATA         0x0207   ///< No data available
    #define ERR_DATA_EXIST      0x0208   ///< Object, data or instance already exists
    #define ERR_COMM_DLL              0x0240 ///< data link layer error (error of rs232 connection)
    #define ERR_COMM_DLL_TIMEOUT      0x0241 ///< timeout during serial operation
    #define ERR_COMM_HW               0x0242 ///< RS232 interface hardware error
    #define ERR_COMM_PROT             0x0243 ///< common protocol error
    #define ERR_COMM_PROT_CRC         0x0244 ///< CRC error
    #define ERR_COMM_PROT_CMD         0x0246 ///< illegal or unknown RS232 command
    #define ERR_COMM_PROT_ACKN        0x0247 ///< receive acknowledge 'F' or no 'O'
    #define ERR_COMM_PROT_DATA_LEN    0x0248 ///< wrong data length code
    #define ERR_CANO_DLL                   0x0300 ///< Data link layer error
    #define ERR_CANO_DLL_HWERR             0x0301 ///< hardware error of CAN controller
    #define ERR_CANO_DLL_TXFULL            0x0302 ///< TX queue of CAN controller is full
    #define ERR_CANO_DLL_WARNING_RX        0x0303 ///< TX error counter (TEC) reached warning level (>96)
    #define ERR_CANO_DLL_WARNING_TX        0x0304 ///< RX error counter (REC) reached warning level (>96)
    #define ERR_CANO_DLL_ERR_PASSIVE       0x0305 ///< CAN "error passive" occurred
    #define ERR_CANO_DLL_BUS_OFF           0x0306 ///< CAN "bus off" error occurred
    #define ERR_CANO_DLL_OVERRUN_RX        0x0307 ///< overrun in RX queue or hardware occurred
    #define ERR_CANO_DLL_OVERRUN_TX        0x0308 ///< overrun in TX queue occurred
    #define ERR_CANO_DLL_CAN_ERR           0x0309 ///< a CAN bit or frame error occurred
    #define ERR_CANO_DLL_ARBITRATION_LOST  0x030A ///< arbitration lost - this is not really an error, its more an event
    #define ERR_CANO_DLL_PHY_FAULT         0x030B ///< General failure of physical layer detected (if supported by hardware)
    #define ERR_CANO_DLL_PHY_H_FAULT       0x030C ///< Fault on CAN-H detected (Low Speed CAN)
    #define ERR_CANO_DLL_PHY_L_FAULT       0x030D ///< Fault on CAN-L detected (Low Speed CAN)
    #define ERR_CANO_DLL_HWSWERR           0x030E ///< Function could not be performed because of hard- or software errors
    #define ERR_CANO_DLL_RES               0x030F ///< Resource error - The resource limit exceeded at creation of a queue or something else
    #define ERR_CANO_DLL_TX                0x0310 ///< A CAN message couldn't be sent for a long time - cable error, wrong baud rate etc.
    #define ERR_CANO_DLL_HW_NOT_FOUND      0x0311 ///< if CAN hardware could not be found - i.e. when detecting USB devices
    #define ERR_CANO_DLL_HW_NOT_AVAILABLE  0x0312 ///< if CAN hardware is detected but could not be used or initialized
    #define ERR_CANO_DLL_SUPP              0x0313 ///< function is not supported this way
    #define ERR_CANO_DLL_PARA              0x0314 ///< Calling parameter(s) is (are) not correct or out of range
    #define ERR_CANO_DLL_CFG               0x0315 ///< Configuration of device failed or configuration not supported
    #define ERR_CANO_DLL_RXQUEUE_EMPTY     0x0316 ///< no message received because RX queue of controller is empty
    #define ERR_CANO_DLL_NOT_INITIALIZED   0x0317 ///< can not send message because hardware is not initialized
    #define ERR_CANO_DLL_BAUDRATE		   0x0318 ///< Desired baud rate is not supported
    #define ERR_CANO_DLL_TIMEOUT           0x0319 ///< timeout executing operation
    #define ERR_CANO_DLL_BUF_OVERFLOW      0x0320 ///< CAN controller buffer overflow errror
    #define ERR_CANO_DLL_CAN_SOCKETERR	   0x0321 ///< Accessing socket
    #define ERR_CANO_CAL                   0x0340  ///< CAN application layer error
    #define ERR_CANO_CAL_NO_DEVICES        0x0341  ///< no devices detected on bus
    #define ERR_CANO_SDO                      0x0400 ///< SDO transfer errors
    #define ERR_CANO_SDO_ABORT                0x0401 ///< SDO transfer aborted
    #define ERR_CANO_SDO_ABORT_TOGGLE_BIT     0x0402 ///< toggle bit not altered
    #define ERR_CANO_SDO_ABORT_TIMEOUT        0x0403 ///< SDO protocol timed out
    #define ERR_CANO_SDO_ABORT_CMD            0x0404 ///< command specifier not valid or unknown
    #define ERR_CANO_SDO_ABORT_BLOCK_SIZE     0x0405 ///< invalid block size in block mode
    #define ERR_CANO_SDO_ABORT_SEQ_NUM        0x0406 ///< invalid sequence number in block mode
    #define ERR_CANO_SDO_ABORT_CRC            0x0407 ///< CRC error (block mode only)
    #define ERR_CANO_SDO_ABORT_OUT_OF_MEM     0x0408 ///< Out of memory
    #define ERR_CANO_SDO_ABORT_UNSUPPORTED    0x0409 ///< unsupported access to an object
    #define ERR_CANO_SDO_ABORT_WRITEONLY      0x040A ///< attempt to read a write only object
    #define ERR_CANO_SDO_ABORT_READONLY       0x040B ///< attempt to write a read only object
    #define ERR_CANO_SDO_ABORT_NOT_EXIST      0x040C ///< Object does not exist
    #define ERR_CANO_SDO_ABORT_NO_MAP         0x040D ///< object cannot be mapped to the PDO
    #define ERR_CANO_SDO_ABORT_MAP_LEN        0x040E ///< number and length of object to be mapped exceeds PDO length
    #define ERR_CANO_SDO_ABORT_PRAM_INCOMP    0x040F ///< general parameter incompatibility reasons
    #define ERR_CANO_SDO_ABORT_DEV_INCOMP     0x0410 ///< general internal incompatibility in device
    #define ERR_CANO_SDO_ABORT_HW             0x0411 ///< access failed due to hardware error
    #define ERR_CANO_SDO_ABORT_TYPE_MISMATCH  0x0412 ///< data type does not match, length of service parameter does not match
    #define ERR_CANO_SDO_ABORT_DATA_LONG      0x0413 ///< data type does not match, length of service parameter too high
    #define ERR_CANO_SDO_ABORT_DATA_SHORT     0x0414 ///< data type does not match, length of service parameter too short
    #define ERR_CANO_SDO_ABORT_SUB_UNKNOWN    0x0415 ///< sub index does not exist
    #define ERR_CANO_SDO_ABORT_VALUE_INVALID  0x0416 ///< invalid value
    #define ERR_CANO_SDO_ABORT_VALUE_HIGH     0x0417 ///< value range of parameter written too high
    #define ERR_CANO_SDO_ABORT_VALUE_LOW      0x0418 ///< value range of parameter written too low
    #define ERR_CANO_SDO_ABORT_MAX_LESS_MIN   0x0419 ///< maximum value is less than minimum value
    #define ERR_CANO_SDO_ABORT_NO_RESOURCE    0x041A ///< Resource not available: SDO connection
    #define ERR_CANO_SDO_ABORT_GENERAL        0x041B ///< general error
    #define ERR_CANO_SDO_ABORT_DATA_TRANSF    0x041C ///< data cannot be transfered or stored to application
    #define ERR_CANO_SDO_ABORT_DATA_LOC_CTRL  0x041D ///< data cannot be transfered or stored to application because of local control
    #define ERR_CANO_SDO_ABORT_DATA_DEV_STATE 0x041E ///< data cannot be transfered or stored to application because of present device state
    #define ERR_CANO_SDO_ABORT_DATA_OD        0x041F ///< object dictionary not present or dynamic generation fails
    #define ERR_CANO_SDO_ABORT_NO_DATA        0x0420 ///< No data available
    #define ERR_CANO_SDO_ABORT_MAN_SPECIFIC   0x04FF ///< manufacturer specific error code
    #define ERR_CANO_LSS_TIMEOUT	          0x0501 ///< LSS communication timed out
    #define ERR_CANO_LSS_NODEID_RANGE         0x0502 ///< Configured node id is out of range error
    #define ERR_CANO_LSS_SWITCH_SELECTIVE     0x0503 ///< LSS slave could not be set to configuration state
    #define ERR_CANO_LSS_MAN_SPECIFIC         0x0504 ///< Manufacturer specific LSS error
    #define ERR_CANO_DEVPROF                    0x0600  ///< device profile specific errors
    #define ERR_DS401                           0x0620  ///< CANopen DS401 specific error codes
    #define ERR_DS402                           0x0640  ///< CANopen DS402 specific error codes
    #define ERR_DS402_TIMEOUT_OPMODE_ACTIVATION 0x0641  ///< Error activating a certain drive operation mode
    #define ERR_DS402_TIMEOUT_STATUSWORD        0x0642  ///< Timeout waiting for status word
    #define ERR_DS402_TIMEOUT_STATUSWORD_PDO    0x0643  ///< Timeout waiting for status word PDO transmission
    #define ERR_DS402_DRV_ENABLE_FAULT_STATE    0x0644  ///< Setting drive into operation enabled state is not possible because drive is in fault state. Clear fault state first
    #define ERR_DS402_DRV_DISABLE_FAULT_STATE   0x0645  ///< Setting drive into operation enabled state is not possible because drive is in fault state. Clear fault state first
    #define ERR_DS402_DRV_ENABLE_TIMEOUT        0x0646  ///< Timeout setting drive to state operation enabled
    #define ERR_DS402_DRV_STATE_FAULT_REACTION  0x0647  ///< Timeout while waiting for the completion of the error reaction time
    #define ERR_DS402_POSITION_RESET            0x0648  ///< Timeout or error resetting position counter
    
    #define ERR_C_ERRNO                         0x4000  ///< Standard C specific errno error codes ored with 0x4000
    #define ERR_APP                             0x8000  ///< application specific errors start here
"""

class _QmixError(object):
    def __init__(self, error_number, dll_dir=None):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'usl.dll')
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
        
    

            
    
#%% INITIALIZATION
if __name__ == '__main__':
    a = QmixBus()
    a.open()
    a.start()
    
    b = QmixPump(index=0)
    c = QmixPump(index=1)
    d = QmixPump(index=2)
    e = QmixPump(index=3)
    
    b.enable()
    c.enable()
    d.enable()
    e.enable()
       
    b.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    c.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    d.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    e.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    
    b.set_volume_unit(prefix="milli", unit="litres")
    c.set_volume_unit(prefix="milli", unit="litres")
    d.set_volume_unit(prefix="milli", unit="litres")
    e.set_volume_unit(prefix="milli", unit="litres")
    
    b.set_syringe_param()
    c.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    d.set_syringe_param()
    e.set_syringe_param()
    
    ch0 = QmixDigitalIO(index=0)
    ch1 = QmixDigitalIO(index=1)
    ch2 = QmixDigitalIO(index=2)
    ch3 = QmixDigitalIO(index=3)
    ch4 = QmixDigitalIO(index=4)
    ch5 = QmixDigitalIO(index=5)
    ch6 = QmixDigitalIO(index=6)
    ch7 = QmixDigitalIO(index=7)

    #TEST3 = QmixPump(index=2)
    #TEST3.enable()
    #TEST3.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    #TEST3.set_volume_unit(prefix="milli", unit="litres")
    #TEST3.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    
    #%% TEST2
    b.valve.current_position
    c.valve.switch_position(position=1)
    c._dll.LCP_Aspirate(c._handle[0], 10, 2)
    d._dll.LCP_SyringePumpCalibrate(d._handle[0])
    c.aspirate(4,2)

    #%% CALIBRATE
    b.calibrate(blocking_wait=False)
    c.calibrate(blocking_wait=False)
    d.calibrate(blocking_wait=False)
    e.calibrate(blocking_wait=False)    
    
    #%% TEST 3
    time.sleep(3)
    ch0.write_on(1)
    time.sleep(1.5)
    ch1.write_on(1)
    time.sleep(1.5)
    ch2.write_on(1)
    time.sleep(1.5)
    ch3.write_on(1)
    time.sleep(1.5)
    ch4.write_on(1)
    time.sleep(1.5)
    ch5.write_on(1)
    time.sleep(1.5)
    ch6.write_on(1)
    time.sleep(1.5)
    ch7.write_on(1)
    time.sleep(1.5)
    
    ch0.write_on(0)
    ch1.write_on(0)
    ch2.write_on(0)
    ch3.write_on(0)
    ch4.write_on(0)
    ch5.write_on(0)
    ch6.write_on(0)
    ch7.write_on(0)
    time.sleep(2.5)
    
    ch0.write_on(1)
    ch1.write_on(1)
    ch2.write_on(1)
    ch3.write_on(1)
    ch4.write_on(1)
    ch5.write_on(1)
    ch6.write_on(1)
    ch7.write_on(1)
    time.sleep(2.5)
    
    ch7.write_on(0)
    time.sleep(1.5)
    ch6.write_on(0)
    time.sleep(1.5)
    ch5.write_on(0)
    time.sleep(1.5)
    ch4.write_on(0)
    time.sleep(1.5)
    ch3.write_on(0)
    time.sleep(1.5)
    ch2.write_on(0)
    time.sleep(1.5)
    ch1.write_on(0)
    time.sleep(1.5)
    ch0.write_on(0)
    time.sleep(1.5)
    
