from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths

import numpy as np
import cv2
import matplotlib.pyplot as plt
from opts import opts
from detectors.ctdet import CtdetDetector

class Maven:
    ''' Class to hold methods and variables for Inference. '''
    
    def __init__(self):
        ''' Method called when object of class is created. '''
        
        # Get options
        self.opt = opts().init()
        self.opt.debug = max(self.opt.debug, 1)

        # Instantiate the Model
        self.detector = CtdetDetector(self.opt)

    def infer(self, data):
        ''' Method to share inferred knowledge '''
        ret = self.detector.run(data)
        return ret['results']
    
