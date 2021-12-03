import numpy as np


def resampling(signal: np.ndarray, resample_parameter: int) -> np.ndarray:
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
