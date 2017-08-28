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
from pphelper.hardware import Trigger

#%% REFACTORING
trigs = {'oil': 10, 'texture':70, 'water':150, 'fixation':220}

T = Trigger(use_threads=False, test_mode=False)
for key in trigs.keys():
    T.add_trigger(key, trigs[key])
      
def run_experiment(conditions=None, block_no=1, n_reps=1, extra_info=None, iti=1, 
                   t_inter_blocks=1, start_from=None, outdir=None):
    """
    This function begins the experiment.
    
    It is possibile to resume an experiment, starting from a specific block.

    Parameters
    ----------
    conditions : str
        Path to the .xlsx file that contains the experiment's conditions.
    
    block_no : int
        Number of blocks that compose the experiment.
        
    n_reps : int
        Number of repetitions per condition (within a block).

    extra_info : dict
        Dictionary containing additional info, e.g.:  participant ID, age, 
        handedness, date and time of the experiment.
        
    iti: int
        Inter trial interval, time between one trial and the next, in seconds.
                  
    t_inter_blocks : int
        Time between one block and the next, in seconds.
               
    start_from : int
        Block number from which to start. Default is None: in this case the 
        experiment will start from the first block.
        
    outdir: str
        path to the output file. Chose a file name and the function will create
        one .tsv file per block, adding as suffix the number of the participant
        and the block.

    Returns
    -------

    """    
    global win
    win = visual.Window(fullscr=True, size=(1920, 1080), monitor='laptop') #TODO: handle in a different way the screen resolution
    instruction1 = visual.TextStim(win, text='A lot of instruction here, blalbablablabla')
    instruction2 = visual.TextStim(win, text='MORE INFO, blalbablablabla')
    instruction1.draw()    
    win.flip()
    core.wait(6,6) #time for instruction1
    instruction2.draw()
    win.flip()
    core.wait(6,6) #time for instruction2
    win.flip()
    
    if start_from is None:
        start = 1
    else: # start from a specific block
        start = start_from
    
    for i in range(start, block_no+1):
        extra_info['block'] = i
        run_block(conditions=conditions, n_reps=n_reps, extra_info=extra_info, 
                  iti=iti, outdir=outdir, block_number=i)
        core.wait(t_inter_blocks, t_inter_blocks)
        
    win.close()


def run_block(conditions, n_reps, extra_info, iti, outdir, block_number):
    trials = data.TrialHandler(conditions, nReps=n_reps, extraInfo=extra_info)
    fixation = visual.TextStim(win, text='+')
    ratingScale = visual.RatingScale(win, precision=10, low=0, high=10, singleClick=True, showAccept=False)
    for trial in trials:
        rating_1, rating_2 = run_trial(trial, fixation, ratingScale)
        trials.addData('INTENSITY', rating_1)
        trials.addData('PLEASANTNESS', rating_2)
        core.wait(iti,iti)
    new_out = outdir + '_' + extra_info['participant'] + '_' + str(block_number)
    trials.saveAsWideText(new_out, appendFile=False)
    print('Ended block ' + str(block_number))
 
    
def run_trial(trial, fixation, ratingScale):
        win.color = [0, 0, 0]
        win.flip()
        win.flip()
        
        #draw fixation cross for a random time between 1.5-2s and send the trigger
        T.select_trigger('fixation')
        fixation.draw()
        T.trigger()
        fixation_duration = np.random.randint(1.5,2) 
        win.flip()
        core.wait(fixation_duration, fixation_duration)
        
        #associate the trial's condition to a syringe pump
        # and dispense the requested amount of volume, then send the trigger
        pump = tastants_pumps[str(trial['taste'])]
        print(str(trial['taste']))
        flow_rate = float(trial['flow_rate'])
        volume = float((trial['volume']))        
        release_time = volume/flow_rate
        
        T.select_trigger(str(trial['taste']))
        pump.dispense(volume, flow_rate)
        T.trigger()
        core.wait(release_time, release_time) #taste release time
        core.wait(2.5) #additional time to avoid visual stimuli
        
        #blank screen
        win.flip()
        core.wait(0.5, 0.5)
        
        #RATING SCALE 1:
        # evaluate intesity
        timer = core.CountdownTimer(3.5)
        ratingScale.setDescription(u'INTENSITÄT')
        while ratingScale.noResponse and timer.getTime()>0:
            ratingScale.draw()
            win.flip()
        rating_1 = ratingScale.getRating()
        if rating_1 is not None:
            rating_1 = round(rating_1)
        print(rating_1)
        ratingScale.reset()
    
        #blank screen
        win.flip()
        core.wait(0.5,0.5)
        
        #RATING SCALE 2:
        # evaluate pleasantness
        timer = core.CountdownTimer(3.5)
        ratingScale.setDescription('ANGENEHMHEIT')
        while ratingScale.noResponse and timer.getTime()>0:
            ratingScale.draw()
            win.flip()
        rating_2 = ratingScale.getRating()
        if rating_2 is not None:
            rating_2 = round(rating_2)
        print(rating_2)
        ratingScale.reset()
        
        #blank screen
        #end of current trial
        win.flip()       
        return rating_1, rating_2 
 
#%% PUMPS INITIALIZATION
if __name__ == '__main__':
    
    qmix_bus = QmixBus()
    qmix_bus.open()
    qmix_bus.start()
    
    pump_2 = QmixPump(index=1)
    pump_3 = QmixPump(index=2)
    pump_4 = QmixPump(index=3)
    pump_5 = QmixPump(index=4)
    pump_6 = QmixPump(index=5)
    pump_2.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    pump_3.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    pump_4.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    pump_5.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    pump_6.set_flow_unit(prefix="milli", volume_unit="litres", time_unit="per_second")
    pump_2.set_volume_unit(prefix="milli", unit="litres")
    pump_3.set_volume_unit(prefix="milli", unit="litres")
    pump_4.set_volume_unit(prefix="milli", unit="litres")
    pump_5.set_volume_unit(prefix="milli", unit="litres")
    pump_6.set_volume_unit(prefix="milli", unit="litres")
    pump_2.set_syringe_param(inner_diameter_mm=23.03, max_piston_stroke_mm=60)
    pump_3.set_syringe_param(inner_diameter_mm=23.03, max_piston_stroke_mm=60)
    pump_4.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    pump_5.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    pump_6.set_syringe_param(inner_diameter_mm=32.5, max_piston_stroke_mm=60)
    
    #%% CALIBRATION 
    ######## REMOVE SYRINGES ########
    pump_2.calibrate(blocking_wait=False)
    pump_3.calibrate(blocking_wait=False)
    pump_4.calibrate(blocking_wait=False)
    pump_5.calibrate(blocking_wait=False)
    pump_6.calibrate(blocking_wait=False)
    
    #%% STOP PUMPS
#    pump_4.stop_all_pumps()
    
    #%% FILL ALL THE SYRINGES
    TEST_FLOW = -2.5
#    pump_4.generate_flow(TEST_FLOW)
    pump_6.generate_flow(TEST_FLOW)
    pump_5.generate_flow(TEST_FLOW)
#  
  
#%% ASPIRATE
    core.wait(8,8)
    pump_2.aspirate(4, 0.2)
    pump_3.aspirate(4, 0.4)
    
#%% DISPENSE
#    core.wait(5,5)
    pump_2.dispense(24.5, 0.78) 
    pump_3.dispense(24.5, 1.3)
    while pump_2.is_pumping or pump_3.is_pumping:
        pass
    pump_2.valve.switch_position(position=0)
    pump_3.valve.switch_position(position=0)
    
    #%% PATHS AND DIRECTORIES
    base_dir =  os.path.normpath('C:\\Users\\758099.INTERN\\Desktop\\neMESYS')
    conditions_file = os.path.join(base_dir, 'fat_taste.xlsx')
    data_dir = os.path.join(base_dir, 'Data_out_fat')
    outfile = os.path.join(data_dir,'output_fat_taste')
    
    #import .xlsx file
    conditions = data.importConditions(conditions_file)
    
    #screen resolution #TODO: not used
    width = GetSystemMetrics(0) 
    height = GetSystemMetrics(1)
    
    #assign to each taste a specific pump
    tastants_pumps = {'oil':pump_6, 'texture':pump_5, 'water':pump_4}
            
    #%% PARTICIPANT INFO
    #Get participant info
    exp_info = dict(participant='001', age=30, handedness=['right', 'left', 'both'],
                    date=data.getDateStr(format='%Y-%m-%d_%H%M'))
    
    r = gui.DlgFromDict(exp_info,
                        order=['participant', 'age', 'handedness', 'date'])
                        
    if not r.OK:
        raise RuntimeError('Info dialog canceled.')
           
    #%% TEST REFACTORING
    run_experiment(conditions=conditions, block_no=1, n_reps=1, 
               extra_info=exp_info, iti=1, t_inter_blocks=1, outdir=outfile)
