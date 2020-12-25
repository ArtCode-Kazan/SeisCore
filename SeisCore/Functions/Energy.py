from math import inf

import numpy as np


def spectrum_energy(spectrum_data: np.ndarray, freq_limits=None) -> float:
    """
    Method for calculating spectral energy
    :param spectrum_data: spectral data (2-D array: first column -
    frequency, second- amplitude)
    :param freq_limits: frequency limits for energy calc
    :return: energy value
    """
    if freq_limits is None:
        f_min, f_max = 0, spectrum_data[-1, 0]
    else:
        f_min, f_max = freq_limits
    selected_spectrum = spectrum_data[(spectrum_data[:, 0] >= f_min) &
                                      (spectrum_data[:, 0] <= f_max)]

    result = np.trapz(x=selected_spectrum[:, 0], y=selected_spectrum[:, 1])
    return result


def amplitude_energy(signal: np.ndarray, norm_coeff=1) -> float:
    """
    Method for calculating energy by amplitude
    :param signal: 1-D array of signal
    :param norm_coeff: norming coefficient for amplitudes
    :return: energy value
    """
    signal = signal / norm_coeff
    signal = signal ** 2
    return np.sum(signal)
