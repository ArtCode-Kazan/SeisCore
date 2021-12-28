import os
import sys
from random import randint

import pytest
import numpy as np


@pytest.fixture()
def load_fast_resampling_function():
    so_file_path = os.path.dirname(__file__)
    sys.path.insert(0, so_file_path)
    from seiscore.binaryfile.resampling import resampling as resample_core
    return resample_core.resampling


@pytest.fixture(params=[0, 1, 2, 10, 30, 100])
def generate_signal(request) -> np.ndarray:
    signal = []
    for _ in range(request.param):
        signal.append(randint(-1000, 1000))
    return np.array(signal, dtype=np.int32)