import os
import sys

import numpy as np


def import_function():
    try:
        so_file_path = os.path.dirname(__file__)
        sys.path.insert(0, so_file_path)
        from seiscore.binaryfile.resampling import resampling as resample_core
        return resample_core.resampling
    except ImportError:
        from seiscore.binaryfile.resampling.origin import resampling
        return resampling


def resampling(arr: np.ndarray, resample_parameter: int) -> np.ndarray:
    function = import_function()
    return function(arr, resample_parameter)
