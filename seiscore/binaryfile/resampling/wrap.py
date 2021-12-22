import os
import sys

import numpy as np

from seiscore.binaryfile.resampling.prototype import resampling as slow_vers


def import_function():
    try:
        so_file_path = os.path.dirname(__file__)
        sys.path.insert(0, so_file_path)
        from seiscore.binaryfile.resampling import resampling as resample_core
        return resample_core.resampling
    except ImportError:
        return slow_vers


def resampling(arr: np.ndarray, resample_parameter: int) -> np.ndarray:
    function = import_function()
    return function(arr, resample_parameter)
