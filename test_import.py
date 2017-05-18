# -*- coding: utf-8 -*-
"""
Created on Thu May 11 11:28:15 2017

@author: alfine-l
"""
import os
from cffi import FFI

_dll_path =      os.path.normpath('C:\Program Files\qmixsdk\labbCAN_Bus_API.dll')
_dll_path_pump = os.path.normpath('C:\Program Files\qmixsdk\labbCAN_Pump_API.dll')

ffi = FFI()
ffi.cdef(
        
        
        """
        typedef long long labb_hdl;      
        typedef long long dev_hdl;        
        long LCB_Open(const char* pDeviceConfigPath);        
        long LCB_Start();        
        long LCB_Stop();        
        long LCB_Close();
        """
)


ffi_pump = FFI()
ffi_pump.cdef(
             """
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
)

# if throws missing .dll error, re-set the pythonpath to C:\Program Files\qmixsdk
_labbCAN_Bus_API_dll = ffi.dlopen(_dll_path)
_labbCAN_Pump_API_dll = ffi_pump.dlopen(_dll_path_pump)


#%% OPEN
path = os.path.normpath('C:/Users/Public/Documents/QmixElements/Projects/test2nemesys/Configurations/nemesys')

test_result_LCB_Open = _labbCAN_Bus_API_dll.LCB_Open(bytes(path,'utf8'))

print(test_result_LCB_Open)


#%% DEVICE HANDLE
pump_handle_1 = ffi.new('dev_hdl *', 0)
pump_handle_2 = ffi.new('dev_hdl *', 0)

#start BUS
_labbCAN_Bus_API_dll.LCB_Start()

# Number of pumps
_labbCAN_Pump_API_dll.LCP_GetNoOfPumps()

# return 0, working
_labbCAN_Pump_API_dll.LCP_LookupPumpByName(bytes("neMESYS_Low_Pressure_1_Pump",'utf8'),pump_handle_1)
_labbCAN_Pump_API_dll.LCP_LookupPumpByName(bytes("neMESYS_Low_Pressure_2_Pump",'utf8'),pump_handle_2)

## We can address by POSITION index (0,1,..N) instead of NAME  (neMESYS_1, .._2, ..._N)
# return 0, working
#_labbCAN_Pump_API_dll.LCP_GetPumpHandle(0,pump_handle_1)
#_labbCAN_Pump_API_dll.LCP_GetPumpHandle(1,pump_handle_2)

# CHECK IF FAULT STATE
return_fault_1 = _labbCAN_Pump_API_dll.LCP_IsInFaultState(pump_handle_1[0])
return_fault_2 = _labbCAN_Pump_API_dll.LCP_IsInFaultState(pump_handle_2[0])
if return_fault_1==1 or return_fault_2==1:
    _labbCAN_Pump_API_dll.LCP_ClearFault(pump_handle_1[0])
    _labbCAN_Pump_API_dll.LCP_ClearFault(pump_handle_2[0])


# ENABLE pumps
_labbCAN_Pump_API_dll.LCP_Enable(pump_handle_1[0])
_labbCAN_Pump_API_dll.LCP_Enable(pump_handle_2[0])


#%% CALIBRATE - REMOVE SYRINGE ! ! !
_labbCAN_Pump_API_dll.LCP_SyringePumpCalibrate(pump_handle_1[0])
_labbCAN_Pump_API_dll.LCP_SyringePumpCalibrate(pump_handle_2[0])


#%% SET VOLUME, PREFIX: -3 = MILLI, 68 = LITRES
_labbCAN_Pump_API_dll.LCP_SetVolumeUnit(pump_handle_1[0], -3, 68) 
_labbCAN_Pump_API_dll.LCP_SetVolumeUnit(pump_handle_2[0], -3, 68)

# SET FLOW UNIT, PREFIX: -3 = MILLI, 68 = LITRES, 1 = PER_SECOND
_labbCAN_Pump_API_dll.LCP_SetFlowUnit(pump_handle_1[0], -3, 68, 1)
_labbCAN_Pump_API_dll.LCP_SetFlowUnit(pump_handle_2[0], -3, 68, 1)


#%% SET SYRINGE PARAMITERS, InnerDIameter_mm, MaxPistonStroke_mm
_labbCAN_Pump_API_dll.LCP_SetSyringeParam(pump_handle_1[0], 23,60)
_labbCAN_Pump_API_dll.LCP_SetSyringeParam(pump_handle_2[0], 23,60)

# MAXIMUM FLOW RATE that is realizable with current dosing unit configuration
flow_rate_max = ffi.new('double *')
_labbCAN_Pump_API_dll.LCP_GetFlowRateMax(pump_handle_1[0], flow_rate_max)
flow_rate_max[0]


#%% ASPIRATE, DISPENSE, PUMPVOLUME (negative values aspirate, positive dipsense)
_labbCAN_Pump_API_dll.LCP_Aspirate(pump_handle_1[0], 10, flow_rate_max[0])
_labbCAN_Pump_API_dll.LCP_PumpVolume(pump_handle_1[0], 15, 1)

# aspirates or dispenses until a certain syringe fill level is reached, 0 indicates completely empty container (eg. empty syringe)
_labbCAN_Pump_API_dll.LCP_SetFillLevel(pump_handle_1[0],0,2)

# generates a constant flow - dosing continues until it gets stopped manually or until pusher reached one of its limits
_labbCAN_Pump_API_dll.LCP_GenerateFlow(pump_handle_1[0], -2)


#%% STOP PUMPS
#specif pump
_labbCAN_Pump_API_dll.LCP_StopPumping(pump_handle_1[0])
#all pumps
_labbCAN_Pump_API_dll.LCP_StopAllPumps()


#%% STATUS FUNCTIONS
p_fill_level = ffi.new('double *')
p_dosed_volume = ffi.new('double *')
p_flow_rate = ffi.new('double *')

_labbCAN_Pump_API_dll.LCP_GetDosedVolume(pump_handle_1[0], p_dosed_volume)
p_dosed_volume[0]

_labbCAN_Pump_API_dll.LCP_GetFillLevel(pump_handle_1[0], p_fill_level)
p_fill_level[0]
 
_labbCAN_Pump_API_dll.LCP_GetFlowIs(pump_handle_1[0], p_flow_rate)
p_flow_rate[0]

_labbCAN_Pump_API_dll.LCP_IsPumping(pump_handle_1[0]) 


#%% PUMP VALVE CONTROL
_labbCAN_Pump_API_dll.LCP_HasValve(pump_handle_1[0])

valve_handle_1 = ffi.new('dev_hdl *')
valve_handle_2 = ffi.new('dev_hdl *')

_labbCAN_Pump_API_dll.LCP_GetValveHandle(pump_handle_1[0], valve_handle_1)
_labbCAN_Pump_API_dll.LCP_GetValveHandle(pump_handle_2[0], valve_handle_2)

valve_handle_1[0]
valve_handle_2[0]

#%% CLOSE
test_result_LCB_Stop = _labbCAN_Bus_API_dll.LCB_Stop()
print(test_result_LCB_Stop)

test_result_LCB_Close = _labbCAN_Bus_API_dll.LCB_Close()
print(test_result_LCB_Close)




