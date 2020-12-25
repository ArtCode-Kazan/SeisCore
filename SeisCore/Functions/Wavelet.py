import warnings

import numpy as np

from pywt import Wavelet, dwt_max_level, wavedec, waverec


def dwt(signal: np.ndarray, level: int) -> np.ndarray:
    """
    Method for forward wavelet transformation with wavelet Dobeshi-10
    :param signal: 1D array of signal
    :param level: transformation level
    :return: list: [cA_n, cD_n, cD_n-1, ..., cD2, cD1]
    (see http://pywavelets.readthedocs.io/en/latest/ref/
                    dwt-discrete-wavelet-transform.html)
    """
    wavelet_type = Wavelet('db10')
    max_levels_count = dwt_max_level(data_len=signal.shape[0],
                                     filter_len=wavelet_type.dec_len)
    if level>max_levels_count:
        warnings.warn('dwt level higher then max allowable level')
        level = max_levels_count

    result = wavedec(signal, 'db10', level=level)
    return result


def idwt(coeffs: list) -> np.ndarray:
    """
    Inverse wavelet transformation with wavelet Dobeshi-10
    :param coeffs: list: [cA_n, cD_n, cD_n-1, ..., cD2, cD1]
    (see http://pywavelets.readthedocs.io/en/latest/ref/
                    dwt-discrete-wavelet-transform.html)
    :return: 1D array of signal
    """
    signal = waverec(coeffs, 'db10')
    signal = np.asarray(signal)
    return signal


def level_num(frequency: float, edge_frequency: float) -> int:
    """
    Function for getting transformation level depending on the edge frequency
    :param frequency: signal frequency
    :param edge_frequency: edge frequency for transformation
    :return: transformation level
    """
    left_lim = frequency
    i = 0
    while True:
        right_lim = left_lim
        left_lim = right_lim / 2
        i += 1
        if left_lim <= edge_frequency <= right_lim:
            if (edge_frequency - left_lim) <= (right_lim - edge_frequency):
                i += 1
            else:
                i -= 1
            break
    return i


def detrend(signal: np.ndarray, frequency: int, edge_frequency: float):
    """
    Method for detrending of signal
    :param signal: 1D-array of signal
    :param frequency: signal frequency
    :param edge_frequency: edge frequency
    :return: массив 1D array with detrend signal
    """
    need_level = level_num(frequency=frequency, edge_frequency=edge_frequency)
    wavelet_data = dwt(signal=signal, level=need_level)
    # An=0
    wavelet_data[0] = np.zeros(wavelet_data[0].shape[0], dtype=np.int)
    detrend_sig = waverec(wavelet_data, 'db10')

    if detrend_sig.shape[0] > signal.shape[0]:
        detrend_sig = detrend_sig[:signal.shape[0]]

    elif detrend_sig.shape[0] < signal.shape[0]:
        zero_count = signal.shape[0] - detrend_sig.shape[0]
        detrend_sig = np.append(detrend_sig, [0] * zero_count)
    return detrend_sig
