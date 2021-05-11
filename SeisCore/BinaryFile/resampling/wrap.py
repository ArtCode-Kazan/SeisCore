import os
import sys

import numpy as np


def resampling(arr: np.ndarray, resample_parameter: int) -> np.ndarray:
    so_file_path = os.path.dirname(__file__)
    sys.path.insert(0, so_file_path)
    from seiscore.binaryfile.resampling import resampling as resample_core
    return resample_core.resampling(arr, resample_parameter)
