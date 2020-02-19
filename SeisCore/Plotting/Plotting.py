import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


plt.switch_backend('SVG')


def plot_graph(x_data, y_data, label, output_folder, output_name,
               x_label=None, y_label=None):
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
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()
    fig.set_size_inches(13, 10)
    fig.dpi = 96

    axes = fig.add_subplot(111)
    x_min = x_data[0]
    x_max = x_data[-1]
    axes.set_xlim(x_min, x_max)

    y_min = np.min(y_data)
    y_max = np.max(y_data)
    axes.set_ylim(y_min, y_max)

    axes.plot(x_data, y_data, lw=1.5, color='#FF0000')

    if x_label is not None:
        axes.set_xlabel(x_label)
    if y_label is not None:
        axes.set_ylabel(y_label)

    axes.set_title(label, fontsize=10)
    plt.grid()

    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)
    plt.close(fig)


def plot_signal(signal, frequency, label, output_folder, output_name,
                time_start_sec=0):
    """
    Method for plotting signal
    :param signal: 1D array of signal
    :param frequency: signal frequency
    :param label: graph label
    :param output_folder: export folder path
    :param output_name: file name of graph
    :param time_start_sec: time in seconds of start signal
    :return:
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()
    fig.set_size_inches(13, 10)
    fig.dpi = 96

    axes = fig.add_subplot(111)

    # Amplitude norming for displaying
    norm_coeff = 1000
    signal = signal/1000

    t_min = time_start_sec
    t_max = time_start_sec+(signal.shape[0] - 1) / frequency
    axes.set_xlim(t_min, t_max)
    axes.set_xticks(np.arange(t_min, t_max + 1, 300))

    amp_min = np.min(signal)
    amp_max = np.max(signal)
    axes.set_ylim(amp_min, amp_max)
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


def plot_average_spectrum(frequency, origin_amplitudes, output_folder,
                          output_name, smooth_amplitudes=None, f_min=None,
                          f_max=None):
    """
    Method for plotting average spectrum
    :param frequency: 1D array of spectrum frequency
    :param origin_amplitudes: 1D array of origin amplitudes
    :param output_folder: export folder path
    :param output_name: export file name
    :param smooth_amplitudes: 1D array of smooth amplitudes (Marmett or
    Median filtration)
    :param f_min: minimal frequency for plotting
    :param f_max:maximal frequency for plotting
    :return:
    """
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    fig = plt.figure()

    fig.set_size_inches(13, 10)
    fig.dpi = 96
    axes = fig.add_subplot(111)

    if f_min is None:
        f_min = frequency[0]
    if f_max is None:
        f_max = frequency[-1]
    axes.set_xlim(f_min, f_max)

    selection_frequency = \
        frequency[(frequency >= f_min) * (frequency <= f_max)]

    selection_origin_amplitudes = \
        origin_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    if smooth_amplitudes is not None:
        selection_smooth_amplitudes = \
            smooth_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

        amp_min = np.min([np.min(selection_origin_amplitudes),
                          np.min(selection_smooth_amplitudes)])
        amp_max = np.max([np.max(selection_origin_amplitudes),
                          np.max(selection_smooth_amplitudes)])
    else:
        amp_min = np.min(selection_origin_amplitudes)
        amp_max = np.max(selection_origin_amplitudes)
        selection_smooth_amplitudes=None

    axes.set_ylim(amp_min, amp_max)
    axes.plot(selection_frequency, selection_origin_amplitudes,
              lw=1, color='#000000',
              label='Average spectrum\n(without smoothing))')
    if smooth_amplitudes is not None:
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
