import numpy as np
from seiscore.binaryfile.resampling import resampling as resample_core


def resampling(arr: np.ndarray, resample_parameter: int) -> np.ndarray:
    return resample_core.resampling(arr, resample_parameter)
