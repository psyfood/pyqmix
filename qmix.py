# -*- coding: utf-8 -*-
"""
Created on Thu May 18 10:58:59 2017

@author: alfine-l
"""
import os
from cffi import FFI


BUS_HEADER =  """
    typedef long long labb_hdl;
    
    typedef long long dev_hdl;
    
    long LCB_Open(const char* pDeviceConfigPath);
    
    long LCB_Start();
    
    long LCB_Stop();
    
    long LCB_Close();
 """

class QmixBus(object):
    def __init__(self, config_dir=None, dll_dir=None):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_Bus_API.dll')

        if config_dir is None:
            self.config_dir = os.path.normpath('C:/Users/Public/Documents/QmixElements/Projects/test2nemesys/Configurations/nemesys')
        else:
            self.config_dir = config_dir
        
        self._ffi = FFI()
        self._ffi.cdef(BUS_HEADER)
        
        self._dll = self._ffi.dlopen(self.dll_file)
        self.is_open = False
        self.is_started = False
        
    def open(self):
        self._dll.LCB_Open(bytes(self.config_dir,'utf8'))
        self.is_open = True
    
    def close(self):
        self._dll.LCB_Close()
        self.is_open = False
    
    def start(self):
        self._dll.LCB_Start()
        self.is_started = True
    
    def stop(self):
        self._dll.LCB_Stop()
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
                     long LCP_Enable(dev_hdl hPump);
                     long LCP_SyringePumpCalibrate(dev_hdl 	hPump);
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
                     """

class QmixPump(object):

    def __init__(self, dll_dir=None, index=0):
        if dll_dir is None:
            self.dll_dir = os.path.normpath('C:/Program Files/qmixsdk')
        else:
            self.dll_dir = dll_dir
            
        self.dll_file = os.path.join(self.dll_dir,
                                 'labbCAN_Pump_API.dll')
        
        self._ffi = FFI()
        self._ffi.cdef( PUMP_HEADER )
                     
                     
        self._dll = self._ffi.dlopen(self.dll_file)
        
        self._handle = self._ffi.new('dev_hdl *', 0)
        self._dll.LCP_GetPumpHandle(index, self._handle)
        
        #?? calibrate works even if enable_pump() is not called. ???
                
    def enable_pump(self):
        self._dll.LCP_Enable(self._handle[0]) 
        
    def is_in_fault_state(self):
        return self._dll.LCP_IsInFaultState(self._handle[0])
    
    def clear_fault_state(self):
        self._dll.LCP_ClearFault(self._handle[0])
        
    def calibrate(self):
        self._dll.LCP_SyringePumpCalibrate(self._handle[0])
        
    def num_pumps(self):
        return self._dll.LCP_GetNoOfPumps()

    def set_volume_unit(self, prefix=-3, volume_unit=68): #-3=MILLI, 68=LITRES
        self._dll.LCP_SetVolumeUnit(self._handle[0], prefix, volume_unit)
        
    def set_flow_unit(self, prefix=-3, volume_unit=68, time_unit=1): #1=PER_SECOND
        self._dll.LCP_SetFlowUnit(self._handle[0], prefix,
                                  volume_unit, time_unit)
        
    def set_syringe_param(self, inner_diameter_mm=23, max_piston_stroke_mm=60):
        self._dll.LCP_SetSyringeParam(self._handle[0], inner_diameter_mm,
                                      max_piston_stroke_mm)
        
    def aspirate(self, volume, flow):
        self._dll.LCP_Aspirate(self._handle[0], volume, flow)

        
