from math import inf

import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy.signal import medfilt
from seiscore.functions.filter import marmett


def spectrum(signal: np.ndarray, frequency: int) -> np.ndarray:
    """
    Method for calculating simple Fourier spectrum of signal
    :param signal: input signal
    :param frequency: signal frequency
    :return: 2D array of spectrum data
    """
    signal_count = signal.shape[0]
    spectrum_data = rfft(signal-np.mean(signal))
    res = np.empty((signal_count // 2 + 1, 2), dtype=np.float)
    res[:, 0] = rfftfreq(signal_count, 1 / frequency)
    res[:, 1] = 2 * abs(spectrum_data) / signal_count
    return res


def average_spectrum(signal: np.ndarray, frequency: int, window: int,
                     offset: int, median_filter=-1,
                     marmett_filter=-1) -> np.ndarray:
    """
    Method for calculating average (cumulative) spectrum
    :param signal: input signal
    :param frequency: signal frequency
    :param window: window size (discreets)
    :param offset: window offset (discreets)
    :param median_filter: median filtration parameter
    :param marmett_filter: marmett filtration parameter
    :return: 2D array of spectrum data
    """
    if median_filter % 2 == 0 or marmett_filter % 2 == 0:
        raise Exception('Marmett and median filters must be odd')

    windows_count = (signal.shape[0] - window) // offset + 1
    # First window position
    left_edge, right_edge = 0, window
    selection_signal = signal[left_edge:right_edge]
    sum_amplitudes = spectrum(selection_signal, frequency)
    sum_amplitudes[:, 1] = np.power(sum_amplitudes[:, 1], 2)
    # median filtration
    if median_filter > 0:
        sum_amplitudes[:, 1] = medfilt(sum_amplitudes[:, 1], median_filter)

    # Other window positions
    for i in range(1, windows_count):
        left_edge, right_edge = i * offset, i * offset + window
        selection_signal = signal[left_edge:right_edge]
        sp_data = np.power(spectrum(selection_signal, frequency)[:, 1], 2)
        if median_filter > 0:
            sp_data = medfilt(sp_data, median_filter)
        sum_amplitudes[:, 1] = sum_amplitudes[:, 1] + sp_data

    # getting average spectrum for all windows
    sum_amplitudes[:, 1] = sum_amplitudes[:, 1] / windows_count

    # marmett filtration
    if marmett_filter > 0:
        sum_amplitudes[:, 1] = marmett(sum_amplitudes[:, 1], marmett_filter)
    return sum_amplitudes


def cepstral_spectrum(spectrum_data, using_log=False) -> np.ndarray:
    """
    Calculating cepstral spectrum from other spectrum data
    :param spectrum_data: 2D array of spectral data: first column -
    frequencies, second - amplitudes
    :param using_log: using log of amplitude
    :return: cepstral spectrum
    """
    if using_log:
        spectrum_data[:, 1] = np.log(spectrum_data[:, 1])

    freq_fictive = 1 / (spectrum_data[1, 0] - spectrum_data[0, 0])
    return spectrum(signal=spectrum_data[:, 1], frequency=freq_fictive)


def nakamura_spectrum(components_spectrum_data, components_order='XYZ',
                      spectrum_type='HV') -> np.ndarray:
    """
    Calculating nakamura spectrum
    :param components_spectrum_data: 2D array: first column - frequencies,
    2,3,4 - components spectral amplitudes
    :param components_order: components order
    :param spectrum_type: spectrum type:
        HV - horizontal/vertical ratio
        VH - vertical/horizontal ratio
    :return: nakamura spectrum
    """
    x_index = components_order.index('X')
    y_index = components_order.index('Y')
    z_index = components_order.index('Z')

    result = np.zeros(shape=(components_spectrum_data.shape[0], 2))
    result[:, 0] = components_spectrum_data[:, 0]
    horizontal_vector = (components_spectrum_data[:, x_index + 1] ** 2 +
                         components_spectrum_data[:, y_index + 1] ** 2) ** 0.5
    vertical_vector = components_spectrum_data[:, z_index + 1]

    if spectrum_type == 'HV':
        bad_indexes = np.argwhere(vertical_vector == 0)
        horizontal_vector[bad_indexes] = 0
        vertical_vector[bad_indexes] = 1
        result[:, 1] = horizontal_vector / vertical_vector
    elif spectrum_type == 'VH':
        bad_indexes = np.argwhere(horizontal_vector == 0)
        vertical_vector[bad_indexes] = 0
        horizontal_vector[bad_indexes] = 1
        result[:, 1] = vertical_vector / horizontal_vector
    return result


def cepstral_spectrum_from_signal(signal: np.ndarray, frequency: int,
                                  using_log=False,
                                  freq_limits=None) -> np.ndarray:
    """
    Calculating cepstral spectrum from other spectrum data
    :param frequency: signal frequency
    :param signal: 1D array of signal data
    :param using_log: using log of amplitude
    :param freq_limits: frequency limits for selection part of signal spectrum
    :return: cepstral spectrum
    """
    sp_data = spectrum(signal=signal, frequency=frequency)
    if freq_limits is None:
        freq_limits = (0, inf)
    sp_data = sp_data[(sp_data[:, 0] >= freq_limits[0]) *
                      (sp_data[:, 0] <= freq_limits[1])]
    return cepstral_spectrum(spectrum_data=sp_data, using_log=using_log)
