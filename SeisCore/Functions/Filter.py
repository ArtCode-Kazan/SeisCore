import numpy as np

from scipy.fftpack import rfft, irfft, rfftfreq


def band_pass_filter(signal: np.ndarray, frequency: int, f_min: float,
                     f_max: float) -> np.ndarray:
    """
    Bandpass filtering
    :param signal: input 1-D array of signal
    :param frequency: signal frequency
    :param f_min: minimal filtering frequency
    :param f_max: maximal filtering frequency
    :return: output 1-D array of signal
    """
    frequency_array = rfftfreq(n=signal.shape[0], d=1.0 / frequency)
    f_signal = rfft(signal)
    f_signal[(frequency_array < f_min) + (frequency_array > f_max)] = 0
    filtered_signal = irfft(f_signal)
    return filtered_signal


def marmett(signal: np.ndarray, order: int) -> np.ndarray:
    """
    Marmett filter
    :param signal: input 1-D array of signal
    :param order: filter order
    :return: output 1-D array of signal
    """
    if order % 2 == 0:
        raise Exception('Invalid order parameter')

    for i in range(order):
        j = 1
        recalculation_array = signal.copy()
        while j < signal.shape[0] - 1:
            recalculation_array[j] = \
                (signal[j - 1] + signal[j + 1]) / 4 + signal[j] / 2
            j += 1
        recalculation_array[0] = (signal[0] + signal[1]) / 2
        recalculation_array[-1] = (signal[-1] + signal[-2]) / 2
        signal = recalculation_array.copy()
    return signal


def sl_function(signal: np.ndarray, frequency: int, long_window=1.0,
                short_window=0.1, order=1) -> np.ndarray:
    """
    Function for getting sta/lta coefficients
    :param signal: 1D array signal data
    :param frequency: signal frequency
    :param long_window: long window (seconds)
    :param short_window: short window (seconds)
    :param order: sl order
    :return: 1D coefficient array
    """
    long_window = int(frequency * long_window)
    short_window = int(frequency * short_window)

    signal = np.abs(signal - np.mean(signal))

    result = np.zeros_like(signal)
    lta_sum, sta_sum = 0, 0
    left_lim = order * long_window
    for i in range(left_lim, signal.shape[0]):
        if i == left_lim:
            lta_sum = np.sum(signal[i - long_window:i])
            sta_sum = np.sum(signal[i - short_window:i])
        else:
            lta_sum = lta_sum - signal[i - long_window - 1] + signal[i - 1]
            sta_sum = sta_sum - signal[i - short_window - 1] + signal[i - 1]
        lta = lta_sum / long_window
        sta = sta_sum / short_window

        if lta == 0:
            val = 0
        else:
            val = sta / lta
        result[i] = val
    return result


def sl_filter(signal, frequency, short_window=0.1, long_window=1.0,
              order=3) -> np.ndarray:
    """
    Function for sta/lta filtration
    :param signal: one-dimension array os signal
    :param frequency: signal frequency
    :param order: filter order
    :param long_window: long window size (seconds)
    :param short_window: short window size (seconds)
    :return: filtered signal (one-dimension array)
    """
    for j in range(order):
        coeffs = sl_function(signal=signal, frequency=frequency,
                             long_window=long_window,
                             short_window=short_window, order=j+1)
        coeffs = (coeffs - np.min(coeffs)) / (np.max(coeffs) - np.min(coeffs))
        signal = signal * coeffs
        signal = signal - np.mean(signal)
    return signal
