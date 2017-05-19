# -*- coding: utf-8 -*-
"""
Created on Thu May 18 10:58:59 2017

@author: alfine-l
"""
import os
from cffi import FFI
import time

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
        
        self._flow_rate_max = self._ffi.new('double *')
        
        self._p_fill_level = self._ffi.new('double *')
        self._p_dosed_volume = self._ffi.new('double *')
        self._p_flow_rate = self._ffi.new('double *')
        
        self._valve_handle = self._ffi.new('dev_hdl *')
               
     #?? calibrate works even if enable_pump() is not called. ???           
    def enable(self):
        self._dll.LCP_Enable(self._handle[0]) 
        
    def is_in_fault_state(self):
        return self._dll.LCP_IsInFaultState(self._handle[0])
    
    def clear_fault_state(self):
        self._dll.LCP_ClearFault(self._handle[0])
        
    def calibrate(self):
        self._dll.LCP_SyringePumpCalibrate(self._handle[0])
        
    def num_pumps(self):
        return self._dll.LCP_GetNoOfPumps()

    def set_volume_unit(self, prefix=None, unit=None): 
        self._dll.LCP_SetVolumeUnit(self._handle[0],
                                    getattr(self._dll, prefix.upper()),
                                    getattr(self._dll, unit.upper()))
        
    def set_flow_unit(self, prefix=None, volume_unit=None, time_unit=None):
        self._dll.LCP_SetFlowUnit(self._handle[0],
                                  getattr(self._dll, prefix.upper()),
                                  getattr(self._dll, volume_unit.upper()),
                                  getattr(self._dll, time_unit.upper()))
    
    # FIND reasonable default parameters
    def set_syringe_param(self, inner_diameter_mm=23, max_piston_stroke_mm=60):
        self._dll.LCP_SetSyringeParam(self._handle[0], inner_diameter_mm,
                                      max_piston_stroke_mm)
    @property    
    def max_flow_rate(self):       
        self._dll.LCP_GetFlowRateMax(self._handle[0], self._flow_rate_max)
        return self._flow_rate_max[0]
        
    def aspirate(self, volume, flow_rate):
        self._dll.LCP_Aspirate(self._handle[0], volume, flow_rate)
        
    def dispense(self, volume, flow_rate):
        self._dll.LCP_Dispense(self._handle[0], volume, flow_rate)
   
#    def pump_volume(self, volume, flow_rate): # NOT WORKING WITH NEGATIVE VALUES, TO FIX
#        self._dll.LCP_PumpVolume(self._handle[0], volume, flow_rate)
        
    def set_fill_level(self, level, flow_rate):
        self._dll.LCP_SetFillLevel(self._handle[0], level, flow_rate)
        
    def generate_flow(self, flow_rate):
        self._dll.LCP_GenerateFlow(self._handle[0], flow_rate)
        
    def stop_pumping(self):
        self._dll.LCP_StopPumping(self._handle[0])
        
    def stop_all_pumps(self): # should be callable without a pump object
        self._dll.LCP_StopAllPumps() #TO FIX
        
    def get_dosed_volume(self): # NOT WORKING, TO FIX
        self._dll.LCP_GetDosedVolume(self._handle, self._p_dosed_volume)
        return self._p_dosed_volume[0]
    
    @property
    def fill_level(self):
        self._dll.LCP_GetFillLevel(self._handle[0], self._p_fill_level)
        return self._p_fill_level[0]

    @property
    def flow_is(self):
        self._dll.LCP_GetFlowIs(self._handle[0], self._p_flow_rate)
        return self._p_flow_rate[0]
    
    def is_pumping(self):
        return self._dll.LCP_IsPumping(self._handle[0]) 
    
    def has_valve(self): #NOT WORKING; returns always 1
        return self._dll.LCP_HasValve(self._handle[0])
    
    def get_valve_handle(self):
        self._dll.LCP_GetValveHandle(self._handle[0], self._valve_handle)
        return self._valve_handle[0]
    
    
#%% TEST
a = QmixBus()
a.open()    
time.sleep(1)
a.start()
time.sleep(1)

b = QmixPump(index=0)
c = QmixPump(index=1)

b.enable()
c.enable()

b.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
c.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")    

b.set_volume_unit(prefix="milli", unit="litres")    
c.set_volume_unit(prefix="milli", unit="litres")   
    
b.set_syringe_param()
c.set_syringe_param()
        
