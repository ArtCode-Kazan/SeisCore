import os
from math import inf

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

from seiscore.plotting.spectrogram import define_step_size


def plot_graph(x_data, y_data, label: str, output_folder: str,
               output_name: str, x_label='x', y_label='y'):
    """
    Method for simple plotting single graph
    :param x_data: 1D array of x-data
    :param y_data: 1D array of y-data
    :param label: graph label
    :param output_folder: output folder path
    :param output_name: output name
    :param x_label: x axis label
    :param y_label: y axis label
    :return:
    """
    plt.switch_backend('SVG')

    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()
    fig.set_size_inches(13, 10)
    fig.dpi = 96

    axes = fig.add_subplot(111)
    axes.set_xlim(x_data[0], x_data[-1])
    axes.set_ylim(np.min(y_data), np.max(y_data))

    axes.plot(x_data, y_data, lw=1.5, color='#FF0000')

    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)

    axes.set_title(label, fontsize=10)
    plt.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)
    plt.close(fig)


def plot_signal(signal: np.ndarray, frequency: int, label: str,
                output_folder: str, output_name: str, time_start_sec=0,
                detail_parameter=800000, norm_coeff=1000):
    """
    Method for plotting signal
    :param signal: 1D array of signal
    :param frequency: signal frequency
    :param label: graph label
    :param output_folder: export folder path
    :param output_name: file name of graph
    :param time_start_sec: time in seconds of start signal
    :param detail_parameter: max points count for drawing graph
    :param norm_coeff: amplitude norming coefficient for plotting
    :return:
    """
    plt.switch_backend('SVG')
    # forced signal resampling only for plotting
    if signal.shape[0] > detail_parameter:
        resample_param = signal.shape[0] // detail_parameter + 1
        signal = signal[::resample_param]
        frequency /= resample_param

    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95
    mpl.rcParams['agg.path.chunksize'] = 10000

    max_time_length_sec = 3600
    base_image_length_inch = 12
    base_image_height_inch = 9
    duration = signal.shape[0] / frequency
    if duration > max_time_length_sec:
        lx = duration / max_time_length_sec * base_image_length_inch
    else:
        lx = base_image_length_inch

    fig = plt.figure()
    fig.set_size_inches(lx, base_image_height_inch)
    fig.dpi = 96

    axes = fig.add_subplot(111)

    # Amplitude norming for displaying
    signal = signal / norm_coeff

    t_min = time_start_sec
    t_max = time_start_sec+(signal.shape[0] - 1) / frequency
    axes.set_xlim(t_min, t_max)

    # tick step depend of signal_duration
    step_size = define_step_size(signal_duration=duration)
    axes.set_xticks(np.arange(t_min, t_max + 1 / frequency, step_size))

    axes.set_ylim(np.min(signal), np.max(signal))
    time_array = np.linspace(start=t_min, stop=t_max, num=signal.shape[0])

    axes.plot(time_array, signal, lw=0.5, color='#FF0000')

    x_label = 'Time, sec'
    y_label = f'Amplitude, c.u x{norm_coeff}'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)

    axes.set_title(label, fontsize=10)

    plt.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)


def plot_average_spectrum(frequency: np.ndarray, origin_amplitudes: np.ndarray,
                          smooth_amplitudes: np.ndarray,
                          output_folder: str, output_name: str,
                          frequency_limits=(0, inf)) -> None:
    """
    Method for plotting average spectrum
    :param frequency: 1D array of spectrum frequency
    :param origin_amplitudes: 1D array of origin amplitudes
    :param output_folder: export folder path
    :param output_name: export file name
    :param smooth_amplitudes: 1D array of smooth amplitudes (Marmett or
    Median filtration)
    :param frequency_limits: frequency limits for plotting
    :return:
    """
    plt.switch_backend('SVG')
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)
    fig.dpi = 96
    axes = fig.add_subplot(111)

    f_min, f_max = frequency_limits
    selection_frequency = \
        frequency[(frequency >= f_min) * (frequency <= f_max)]

    selection_origin_amplitudes = \
        origin_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    selection_smooth_amplitudes = \
        smooth_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    amp_min = np.min([np.min(selection_origin_amplitudes),
                      np.min(selection_smooth_amplitudes)])
    amp_max = np.max([np.max(selection_origin_amplitudes),
                      np.max(selection_smooth_amplitudes)])

    axes.set_xlim(selection_frequency[0], selection_frequency[-1])
    axes.set_ylim(amp_min, amp_max)
    axes.plot(selection_frequency, selection_origin_amplitudes,
              lw=1, color='#000000',
              label='Average spectrum\n(without smoothing))')
    axes.plot(selection_frequency, selection_smooth_amplitudes,
              lw=2, color='#FF0000',
              label='Average spectrum\n(with smoothing)')

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    x_label = 'Frequency, Hz'
    y_label = 'Amplitude, c.u'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)

    axes.set_title(output_name, fontsize=10)

    axes.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    plt.close(fig)
