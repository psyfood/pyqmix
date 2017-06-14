# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:58:27 2017

@author: alfine-l
"""
#%%
from __future__ import division, print_function
import numpy as np
import os
import sys
from psychopy import core, data, event, visual# , gui 

sys.path.append("L:\\PSY-Studenten\\Lorenzo\\Python Scripts\\gustometer")
from qmix import QmixBus, QmixPump, QmixError

base_dir =  os.path.normpath('L:\PSY-Studenten\Lorenzo\Python Scripts\PsychoPy')
conditions_file = os.path.join(base_dir, 'qmix_conditions.xlsx')

# Load conditions file.
conditions = data.importConditions(conditions_file)
print(conditions)
trials = data.TrialHandler(conditions, nReps=5)
