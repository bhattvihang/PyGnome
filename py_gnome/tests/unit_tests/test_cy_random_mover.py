"""
unit tests cython wrapper

designed to be run with py.test
"""

import numpy as np

from gnome import basic_types
from gnome.cy_gnome import cy_random_mover
from gnome.utilities import time_utils

import datetime

import pytest


def test_exceptions():
    """
    Test ValueError exception thrown if improper input arguments
    """
    with pytest.raises(ValueError):
        cy_random_mover.CyRandomMover(diffusion_coef=0)

class Common():
    """
    test setting up and moving four particles
    
    Base class that initializes stuff that is common for multiple cy_wind_mover objects
    """
    
    #################
    # create arrays #
    #################
    num_le = 4  # test on 4 LEs
    ref  =  np.zeros((num_le,), dtype=basic_types.world_point)   # LEs - initial locations
    status = np.empty((num_le,), dtype=basic_types.status_code_type)
    
    time_step = 60
    
    def __init__(self):
        time = datetime.datetime(2012, 8, 20, 13)
        self.model_time = time_utils.date_to_sec( time)
        ################
        # init. arrays #
        ################
        self.ref[:] = 1.
        self.ref[:]['z'] = 0 # on surface by default
        self.status[:] = basic_types.oil_status.in_water
    
class TestRandom():
    cm = Common()
    rm = cy_random_mover.CyRandomMover(diffusion_coef=100000)    
    delta = np.zeros((cm.num_le,), dtype=basic_types.world_point)
    def move(self, delta): 
        self.rm.prepare_for_model_run()
        
        self.rm.prepare_for_model_step(self.cm.model_time, self.cm.time_step)
        self.rm.get_move( self.cm.model_time,
                          self.cm.time_step, 
                          self.cm.ref,
                          delta,
                          self.cm.status,
                          basic_types.spill_type.forecast,
                          0)
        
    def test_move(self):
        self.move(self.delta)
        print self.delta
        assert np.all(self.delta['lat'] != 0)
        assert np.all(self.delta['long'] != 0)
        
    def test_zero_coef(self):
        """
        ensure no move for 0 diffusion coefficient 
        """
        self.rm.diffusion_coef = 0
        new_delta = np.zeros((self.cm.num_le,), dtype=basic_types.world_point)
        self.move(new_delta)
        self.rm.diffusion_coef = 100000        
        assert np.all(new_delta.view(dtype=np.double).reshape(1,-1) == 0)
        
    def test_update_coef(self):
        """
        For now just test that the move is different from original move
        """
        self.rm.diffusion_coef = 10
        assert self.rm.diffusion_coef == 10 
        
        new_delta = np.zeros((self.cm.num_le,), dtype=basic_types.world_point)
        self.move(new_delta)
        print self.delta
        print new_delta
        assert np.all(self.delta['lat'] != new_delta['lat'])
        assert np.all(self.delta['long'] != new_delta['long'])
        
    
if __name__ == "__main__":
    """
    This makes it easy to use this file to debug the lib_gnome DLL 
    through Visual Studio
    """
    tr = TestRandom()
    tr.test_move()
    tr.test_update_coef()
