import numpy as np
cimport numpy as np
cimport cython


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def resampling(np.ndarray[np.int32_t, ndim=1] signal,
               int resample_parameter):
    """
    Method for signal resampling
    :param signal: 1D array of signal
    :param resample_parameter: resample factor
    :return: 1D array of resample signal
    """
    cdef:
        # Origin signal size
        int discrete_amount
        # Resample signal size
        int resample_discrete_amount
        # Iteration variables
        int i, j, k
        int sum_a, sum_b, sum_c
        int value_a, value_b, value_c
        # Output array
        np.ndarray[np.int32_t, ndim = 1] resample_signal

    discrete_amount = signal.shape[0]
    resample_discrete_amount = discrete_amount // resample_parameter

    resample_signal = np.zeros(shape=resample_discrete_amount, dtype=np.int32)
    for i in range(resample_discrete_amount):
        sum_val = 0
        for j in range(resample_parameter):
            k = i * resample_parameter + j
            sum_val += signal[k]
        value = sum_val // resample_parameter
        resample_signal[i] = value
    return resample_signal
