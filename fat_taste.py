# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 12:33:29 2017

@author: alfine-l
"""
from __future__ import division, print_function
from win32api import GetSystemMetrics
import numpy as np
import os
from psychopy import core, data, event, gui, visual 
from qmix import QmixBus, QmixPump, _QmixError, QmixDigitalIO
import pandas as pd

#%% PUMPS INITIALIZATION
qmix_bus = QmixBus()
qmix_bus.open()
qmix_bus.start()

pump_4 = QmixPump(index=3)
pump_5 = QmixPump(index=4)
pump_6 = QmixPump(index=5)
pump_4.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_5.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_6.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
pump_4.set_volume_unit(prefix="milli", unit="litres")
pump_5.set_volume_unit(prefix="milli", unit="litres")
pump_6.set_volume_unit(prefix="milli", unit="litres")
pump_4.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
pump_5.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
pump_6.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)

#%% CALIBRATION
pump_4.calibrate(blocking_wait=False)
pump_5.calibrate(blocking_wait=False)
pump_6.calibrate(blocking_wait=False)

#%% FILL ALL THE SYRINGES
pump_4.generate_flow(-4)
pump_5.generate_flow(-4)
pump_6.generate_flow(-4)
    
#%% PATHS AND DIRECTORIES
base_dir =  os.path.normpath('L:\PSY-Studenten\Lorenzo\Python Scripts\gustometer')
conditions_file = os.path.join(base_dir, 'fat_taste.xlsx')
data_dir = os.path.join(base_dir, 'Data_out_fat')
outfile = os.path.join(data_dir,'output_fat_taste')

#import .xlsx file
conditions = data.importConditions(conditions_file)

#screen resolution
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)

#assign to each taste a specific pump
tastants_pumps = {'oil':pump_6, 'texture':pump_5, 'water':pump_4}

#%% FUNCTIONS
def perform_trial(conditions=None, nReps=0, extraInfo=None, block_number=None, out_dir=None):
    win = visual.Window(fullscr=True, size=(1920, 1080), monitor='laptop')
    trials = data.TrialHandler(conditions, nReps=nReps, extraInfo=extraInfo)
    fixation = visual.TextStim(win, text='+')
    ratingScale = visual.RatingScale(win, precision=10, low=0, high=10, singleClick=True, showAccept=False)
    for trial in trials:
        win.color = [0, 0, 0]
        win.flip()
        win.flip()
        
        #draw fixation cross for a random time between 1.5-2s
        fixation.draw()
        fixation_duration = np.random.randint(1.5,2) 
        win.flip()
        core.wait(fixation_duration,fixation_duration)
        
        #associate the trial's condition to a syringe pump
        # and dispense the requested amount of volume
        pump = tastants_pumps[str(trial['taste'])]
        print(str(trial['taste']))
        flow_rate = float(trial['flow_rate'])
        volume = float((trial['volume']))
        
        pump.dispense(volume, flow_rate)
        core.wait(1.5,1.5) #taste release time
        core.wait(2.5) #additional time to avoid visual stimuli
        
        #blank screen
        win.flip()
        core.wait(0.5,.5)
        
        #RATING SCALE:
        # evaluate intesity
        timer = core.CountdownTimer(3.5)
        ratingScale.setDescription('INTENSITAT') #TODO: Ä not supported
        while ratingScale.noResponse and timer.getTime()>0:
            ratingScale.draw()
            win.flip()
        rating = ratingScale.getRating()
        if rating is not None:
            rating = round(rating)
        print(rating)
        trials.addData('INTENSITAT', rating) #TODO: Ä not supported
        ratingScale.reset()
    
        #blank screen
        win.flip()
        core.wait(0.5,0.5)
        
        #RATING SCALE:
        # evaluate pleasentness
        timer = core.CountdownTimer(3.5)
        ratingScale.setDescription('ANGENEHMHEIT')
        while ratingScale.noResponse and timer.getTime()>0:
            ratingScale.draw()
            win.flip()
        rating = ratingScale.getRating()
        if rating is not None:
            rating = round(rating)
        print(rating)
        trials.addData('ANGENEHMHEIT', rating)
        ratingScale.reset()
        
        #blank screen
        #end of current trial
        win.flip()       
        core.wait(6,6)    
    
    win.close()
    #Save the data from the trial to .xlsx file document.
#    trials.saveAsExcel(fileName=out_dir, sheetName=extraInfo['participant']+'_'+str(block_number), 
#                       appendFile=True, dataOut=('n','all_raw'))
    new_out = outfile + '_' + str(block_number) + '.xlsx'
    trials_data = trials.saveAsWideText(new_out)
    writer = pd.ExcelWriter(new_out)
    trials_data.to_excel(writer)
    writer.save()

global win_instruction
def start_blocks(n_blocks=0, t_inter_blocks=None,conditions=None, nReps=0,
                 extraInfo=None, start_from=None, out_dir=None):
    
    #Instruction for the participant
    win_instruction = visual.Window(fullscr=True, size=(1920, 1080), monitor='laptop')
    instruction1 = visual.TextStim(win_instruction, text='A lot of instruction here, blalbablablabla')
    instruction2 = visual.TextStim(win_instruction, text='MORE INFO, blalbablablabla')
    instruction1.draw()    
    win_instruction.flip()
    core.wait(6,6)
    instruction2.draw()
    win_instruction.flip()
    core.wait(6.6)
    win_instruction.flip() #for smooth transition win_instruction - win trial/ block-block

    if start_from is None:
        start = 1
    else:
        start = start_from
    
    for i in range(start, n_blocks+1):
        extraInfo['block'] = i
        perform_trial(conditions=conditions, nReps=nReps, extraInfo=extraInfo,block_number=i, out_dir=out_dir)
        core.wait(t_inter_blocks,t_inter_blocks)
        
    win_instruction.close()
        
        
#%% PARTICIPANT INFO
#Get participant info.
exp_info = dict(participant='001', age=30, handedness=['right', 'left', 'both'],
                date=data.getDateStr(format='%Y-%m-%d_%H%M'))

r = gui.DlgFromDict(exp_info,
                    order=['participant', 'age', 'handedness', 'date'])
                    
if not r.OK:
    raise RuntimeError('Info dialog canceled.')
    
#%% TEST
start_blocks(n_blocks=2,t_inter_blocks=2,conditions=conditions, nReps=3, extraInfo=exp_info, out_dir=outfile)
