import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy.signal import medfilt
from SeisCore.Functions.Filter import marmett


def spectrum(signal, frequency):
    """
    Method for calculating simple Fourier spectrum of signal
    :param signal: input signal
    :param frequency: signal frequency
    :return: 2D array of spectrum data
    """
    signal_count = signal.shape[0]
    spectrum_data = rfft(signal)
    res = np.empty((signal_count // 2 + 1, 2), dtype=np.float)
    res[:, 0] = rfftfreq(signal_count, 1 / frequency)
    res[:, 1] = 2 * abs(spectrum_data) / signal_count
    return res


def average_spectrum(signal, frequency, window, offset,
                     med_filter=None, marmett_filter=None):
    """
    Method for calculating average (cumulative) spectrum
    :param signal: input signal
    :param frequency: signal frequency
    :param window: window size (discreets)
    :param offset: window offset (discreets)
    :param med_filter: median filtration parameter
    :param marmett_filter: marmett filtration parameter
    :return: 2D array of spectrum data
    """
    windows_count = (signal.shape[0] - window) // offset + 1

    # First window position
    left_edge = 0
    right_edge = window
    selection_signal = signal[left_edge:right_edge]
    sum_a = spectrum(selection_signal, frequency)
    sum_a[:, 1] = np.power(sum_a[:, 1], 2)
    # median filtration
    if med_filter is not None:
        sum_a[:, 1] = medfilt(sum_a[:, 1], med_filter)

    # Other window positions
    for i in range(1, windows_count):
        left_edge = i * offset
        right_edge = left_edge + window
        selection_signal = signal[left_edge:right_edge]
        sp_data = np.power(spectrum(selection_signal, frequency)[:, 1], 2)
        if med_filter is not None:
            sp_data = medfilt(sp_data, med_filter)
        sum_a[:, 1] = sum_a[:, 1] + sp_data

    # getting average spectrum for all windows
    sum_a[:, 1] = sum_a[:, 1] / windows_count

    # marmett filtration
    if marmett_filter is not None:
        sum_a[:, 1] = marmett(sum_a[:, 1], marmett_filter)
    return sum_a


def cepstral_spectrum(spectrum_data, using_log=False):
    """
    Calculating cepstral spectrum from other spectrum data
    :param spectrum_data: 2D array of spectral data: first column -
    frequencies, second - amplitudes
    :param using_log: using log of amplitude
    :return: cepstral spectrum
    """
    if using_log:
        spectrum_data[:,1]=np.log(spectrum_data[:,1])

    freq_fictive=1/(spectrum_data[1,0]-spectrum_data[0,0])
    result=spectrum(signal=spectrum_data[:,1], frequency=freq_fictive)
    return result


def nakamura_spectrum(components_spectrum_data, components_order='XYZ',
                      spectrum_type='HV'):
    """
    Calculating nakamura spectrum
    :param components_spectrum_data: 2D array: first column - frequencies,
    2,3,4 - components spectral ampolitudes
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
        horizontal_vector[bad_indexes] = -9999.25
        vertical_vector[bad_indexes] = 1
        result[:, 1] = horizontal_vector / vertical_vector
    elif spectrum_type == 'VH':
        bad_indexes = np.argwhere(horizontal_vector == 0)
        vertical_vector[bad_indexes] = -9999.25
        horizontal_vector[bad_indexes] = 1
        result[:, 1] = vertical_vector / horizontal_vector
    return result


def cepstral_spectrum_from_signal(signal, frequency, using_log=False):
    """
    Calculating cepstral spectrum from other spectrum data
    :param frequency: signal frequency
    :param signal: 1D array of signal data
    :param using_log: using log of amplitude
    :return: cepstral spectrum
    """
    sp_data=spectrum(signal=signal, frequency=frequency)
    return cepstral_spectrum(spectrum_data=sp_data, using_log=using_log)
