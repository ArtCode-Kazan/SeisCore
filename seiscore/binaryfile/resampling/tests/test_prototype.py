import pytest
from hamcrest import assert_that, equal_to

import numpy as np

from seiscore.binaryfile.resampling.prototype import resampling


@pytest.mark.parametrize(
    'signal, resample_param, expected',
    [(np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=np.int32), 4,
      np.array([1, 1, 1], dtype=np.int32)),
     (np.array([], dtype=np.int32), 4, np.array([], dtype=np.int32)),
     (np.array([1, 2, 3, 4, 5], dtype=np.int32), 1,
      np.array([1, 2, 3, 4, 5], dtype=np.int32)),
     (np.array([2, 4, 4, 6, 6, 8], dtype=np.int32), 2,
      np.array([3, 5, 7], dtype=np.int32)),
     (np.array([1, 4, 3, 6, 5, 8], dtype=np.int32), 2,
      np.array([2, 4, 6], dtype=np.int32))
     ])
def test_resampling(signal, resample_param, expected):
    fact = resampling(signal, resample_param)
    assert_that(all(fact == expected), equal_to(True))
