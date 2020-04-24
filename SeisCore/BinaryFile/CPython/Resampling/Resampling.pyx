import numpy as np
cimport numpy as np
cimport cython


np.import_array()

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def resampling(np.ndarray[np.int32_t, ndim=2] signal,
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
        # Iteration varables
        int i, j, k
        int sum_a, sum_b, sum_c
        int value_a, value_b, value_c
        # Output array
        np.ndarray[np.int32_t, ndim = 2] resample_signal

    discrete_amount = signal.shape[0]
    resample_discrete_amount = discrete_amount // resample_parameter

    resample_signal = np.empty(shape=(resample_discrete_amount,3),
                               dtype=np.int32)

    for i in range(resample_discrete_amount):
        sum_a = sum_b = sum_c = 0
        for j in range(resample_parameter):
            k = i * resample_parameter + j
            sum_a = sum_a + signal[k, 0]
            sum_b = sum_b + signal[k, 1]
            sum_c = sum_c + signal[k, 2]
        value_a = sum_a // resample_parameter
        value_b = sum_b // resample_parameter
        value_c = sum_c // resample_parameter
        resample_signal[i,:] = np.array([value_a, value_b, value_c])
    return resample_signal
