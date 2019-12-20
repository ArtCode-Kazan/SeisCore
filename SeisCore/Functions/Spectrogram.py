from scipy import signal
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import warnings
import os


plt.switch_backend('SVG')


def specgram(signal_data, frequency_of_signal,
             min_frequency=None, max_frequency=None, time_start=0):
    """
    Method for calculation spectrogram data
    :param signal_data: 1D-array of signal data
    :param frequency_of_signal: signal frequency
    :param min_frequency: low cut frequency for spectrogram visualization
    :param max_frequency: high cut frequency for spectrogram visualization
    :param time_start: time difference (in seconds) between signal
    start time and spectrogram analysis start time
    :return: tuple with time(seconds), frequencies(Hz), amplitudes(dB)
    """
    # Kaiser window creation:
    # M=2048 beta=5 sym=false
    window_kaiser = signal.windows.kaiser(2048, 5, False)

    # spectrogram window
    nfft_window_size = 8192
    # noverlap of window
    noverlap_size = 1792    # 2048-256

    if signal_data.shape[0]<=window_kaiser.shape[0]:
        return None

    f, t, s = signal.spectrogram(x=signal_data,
                                 fs=frequency_of_signal,
                                 window=window_kaiser,
                                 nfft=nfft_window_size,
                                 noverlap=noverlap_size)

    # correction time
    t = t + time_start

    if min_frequency is None:
        min_frequency = 0
    if max_frequency is None:
        max_frequency = frequency_of_signal/2

    # amplitudes selection
    ds = s[((min_frequency <= f)*(f <= max_frequency))]

    # frequencies selection
    df = f[((min_frequency <= f)*(f <= max_frequency))]
    return t, df, ds


def scale_limits(amplitudes, frequencies=None, low_f=None, high_f=None):
    """
    Method for defining spectrogram scale limits
    :param amplitudes: spectrogram amplitude matrix
    :param frequencies: array of frequency
    :param low_f: low cut frequency
    :param high_f: high cut frequency
    :return: scale limits
    """
    if frequencies is not None:
        if low_f is None:
            low_f = 0
        if high_f is None:
            high_f = frequencies[-1]
        amplitudes = amplitudes[((low_f <= frequencies) & (frequencies <= high_f))]

    mid_amp = abs(amplitudes).mean()
    # dispersion sum for each time interval
    disp_sum = 0
    for i in range(amplitudes.shape[1]):
        d = np.std(abs(amplitudes[:, i]) - mid_amp)
        disp_sum += d
    # average dispersion value
    disp_average = disp_sum / amplitudes.shape[1]

    # minimal scale value (dB)
    bmin = 20 * np.log10(abs(np.min(amplitudes)))
    # maximal scale value (dB)
    bmax = 20 * np.log10(mid_amp + 9 * disp_average)
    return bmin, bmax


def get_scale(amplitudes):
    """
    Method for getting scale parameters (matplotlib)
    :param amplitudes: amplitude matrix (dB)
    :return: colormap parameters
    """
    bmin, bmax = scale_limits(amplitudes=amplitudes)
    levels = MaxNLocator(nbins=100).tick_values(bmin, bmax)
    cmap = plt.get_cmap('jet')
    norm = BoundaryNorm(boundaries=levels, ncolors=cmap.N, clip=False)
    return cmap, norm


def plot(times, frequencies, amplitudes, cmap, cnorm,output_folder,
         output_name):
    """
    Method for spectrogram export to png file
    :param times: time 1D-array (seconds)
    :param frequencies: frequency 1D-array(Hz)
    :param amplitudes: amplitude matrix
    :param cmap: colormap
    :param cnorm: colormap levels
    :param output_folder: output folder
    :param output_name: output file name
    """
    warnings.filterwarnings("ignore")

    # document field offset
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    # calc document size in inches (depend on time duration)
    ly = 9
    if np.max(times)-np.min(times) > 3600:
        lx = 12 / 3600 * (np.max(times)-np.min(times))
    else:
        lx = 12

    fig.set_size_inches(lx, ly)

    fig.dpi = 96
    axes = fig.add_subplot(111)

    # decibels calculation
    amplitudes=20 * np.log10(abs(amplitudes))

    axes.pcolormesh(times, frequencies, 20 * np.log10(abs(amplitudes)),
                    cmap=cmap, norm=cnorm)

    x_label = 'Time, s'
    y_label = 'Frequency, Hz'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)

    axes.set_title(output_name, fontsize=10)

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)
    plt.close(fig)


def create_spectrogram(signal_data, frequency, output_folder, output_name,
                       min_frequency=None, max_frequency=None, time_start=0):
    """
    Simple method for creating and exporting spectrogram to png file
    :param signal_data: 1D-array of signal data
    :param frequency: signal frequency
    :param output_folder: export folder path
    :param output_name: output file name (without extension)
    :param min_frequency: low cut frequency for spectrogram visualization
    :param max_frequency: high cut frequency for spectrogram visualization
    :param time_start: time difference (in seconds) between signal
    start time and spectrogram analysis start time
    """
    result = specgram(signal_data=signal_data, frequency_of_signal=frequency,
                      min_frequency=min_frequency,
                      max_frequency=max_frequency, time_start=time_start)

    if result is None:
        return

    t, f, amplitudes = result
    cmap, cnorm = get_scale(amplitudes=amplitudes)

    plot(times=t, frequencies=f, amplitudes=amplitudes, cmap=cmap,
         cnorm=cnorm, output_folder=output_folder, output_name=output_name)
