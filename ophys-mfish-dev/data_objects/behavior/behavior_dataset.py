from data_objects.behavior.grab_behavior import GrabBehavior
from data_objects.stimulus import stimulus_processing
from data_objects.sync import sync_utilities

from typing import Any, Optional
import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import h5py
import numpy as np
import xarray as xr
from .. import data_processing_keys as keys

# OPHYS_KEYS = ('2p_vsync', 'vsync_2p')

# STIMULUS_KEYS = ('frames', 'stim_vsync', 'vsync_stim')
# PHOTODIODE_KEYS = ('photodiode', 'stim_photodiode')
# EYE_TRACKING_KEYS = ("eye_frame_received",  # Expected eye tracking
#                                             # line label after 3/27/2020
#                         # clocks eye tracking frame pulses (port 0, line 9)
#                         "cam2_exposure",
#                         # previous line label for eye tracking
#                         # (prior to ~ Oct. 2018)
#                         "eyetracking",
#                         "eye_cam_exposing",
#                         "eye_tracking")  # An undocumented, but possible eye tracking line label  # NOQA E114
# BEHAVIOR_TRACKING_KEYS = ("beh_frame_received",  # Expected behavior line label after 3/27/2020  # NOQA E127
#                                                  # clocks behavior tracking frame # NOQA E127
#                                                  # pulses (port 0, line 8)
#                             "cam1_exposure",
#                             "behavior_monitoring")


class LazyLoadable(object):
    def __init__(self, name, calculate):
        ''' Wrapper for attributes intended to be computed or loaded once, 
        then held in memory by a containing object.

        Parameters
        ----------
        name : str
            The name of the hidden attribute in which this attribute's data will be stored.
        calculate : fn
            a function (presumably expensive) used to calculate or load this attribute's data

        '''

        self.name = name
        self.calculate = calculate

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not hasattr(obj, self.name):
            setattr(obj, self.name, self.calculate(obj))
        return getattr(obj, self.name)


class BehaviorDataset(GrabBehavior):
    """Includes stimulus, tasks, biometrics"""
    def __init__(self, 
                 raw_folder_path: Optional[str] = None, # where sync file is (pkl file)
                 oeid: Optional[str] = None,
                 data_path: Optional[str] = None):
        super().__init__(raw_folder_path=raw_folder_path,
                         oeid=oeid,
                         data_path=data_path)

    def get_stimulus_timestamps(self): 
        self._stimulus_timestamps = sync_utilities.get_synchronized_frame_times(
            session_sync_file=self.file_paths['sync_file'],
            sync_line_label_keys=keys.STIMULUS_KEYS,
            drop_frames=None,
            trim_after_spike=True)
        print("STIMMY")

        return self._stimulus_timestamps

    def get_stimulus_presentations(self):
        pkl_file_path = self.file_paths['stimulus_pkl']
        pkl_data = pd.read_pickle(pkl_file_path)

        self._stimulus_presentations = stimulus_processing.get_stimulus_presentations(
            pkl_data, self.stimulus_timestamps)

        return self._stimulus_presentations

    # lazy load
    stimulus_presentations = LazyLoadable('_stimulus_presentations', get_stimulus_presentations)
    stimulus_timestamps = LazyLoadable('_stimulus_timestamps', get_stimulus_timestamps)