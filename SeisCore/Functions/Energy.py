import numpy as np


def spectrum_energy(spectrum_data, f_min, f_max):
    """
    Method for calculating spectral energy
    :param spectrum_data: spectral data (2-D array: first column -
    frequency, second- amplitude)
    :param f_min: minimal frequency for energy calc
    :param f_max: maximal frequency for energy calc
    :return: energy value
    """
    if f_min is None:
        f_min = min(spectrum_data[:, 0])
    if f_max is None:
        f_max = max(spectrum_data[:, 0])
    selected_spectrum = spectrum_data[(spectrum_data[:, 0] >= f_min) &
                                      (spectrum_data[:, 0] <= f_max)]

    result = np.trapz(x=selected_spectrum[:, 0], y=selected_spectrum[:, 1])
    return result


def amplitude_energy(signal, norm_coeff=1):
    """
    Method for calculating energy by amplitude
    :param signal: 1-D array of signal
    :param norm_coeff: norming coefficient for amplitudes
    :return: energy value
    """
    signal = signal / norm_coeff
    signal = signal ** 2
    return np.sum(signal)
