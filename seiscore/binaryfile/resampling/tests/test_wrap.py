import pytest
from hamcrest import assert_that, equal_to


import numpy as np

from seiscore.binaryfile.resampling.prototype import resampling as slow_vers


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
def test_fast_resampling(signal, resample_param, expected,
                         load_fast_resampling_function):
    function = load_fast_resampling_function
    fact = function(signal, resample_param)
    assert_that(all(fact == expected), equal_to(True))


def test_fast_with_low_resampling(generate_signal,
                                  load_fast_resampling_function):
    fast_function = load_fast_resampling_function
    expected = slow_vers(generate_signal, resample_parameter=4)
    fact = fast_function(generate_signal, resample_parameter=4)
    assert_that(all(fact == expected), equal_to(True))
