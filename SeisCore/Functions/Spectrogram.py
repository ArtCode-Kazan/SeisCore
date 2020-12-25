import warnings
import os
from typing import NamedTuple

import numpy as np

from scipy import signal

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


class SpData(NamedTuple):
    times: np.ndarray = np.array([0])
    frequencies: np.ndarray = np.array([0])
    amplitudes: np.ndarray = np.array([0])


class Spectrogram:
    def __init__(self, signal_arr: np.ndarray, frequency: int,
                 time_start=0., freq_limits=None):
        self.signal = signal_arr
        self.frequency = frequency
        self.time_start = time_start
        if freq_limits is None:
            self.freq_limits = (0, frequency/2)
        else:
            self.freq_limits = freq_limits

        # Kaiser window creation:
        # M=2048 beta=5 sym=false
        self._window_kaiser = signal.windows.kaiser(2048, 5, False)

        # spectrogram window
        self._nfft_window_size = 8192
        # noverlap of window 1792=2048-256
        self._noverlap_size = 1792

        # spectrograms data (tuple freq_array, times_array, amplitudes)
        self._sp_data: SpData = SpData()

        # document plot parameters
        self.spectrogram_size_x_inch, self.spectrogram_size_y_inch = 12, 9
        self.max_time_length_sec = 3600

    def _spectrogram_calc(self):
        """
        Method for calculation spectrogram data
        :return: tuple with time(seconds), frequencies(Hz), amplitudes(dB)
        """
        if self.signal.shape[0] <= self._window_kaiser.shape[0]:
            raise Exception('Signal size less then Kaiser window')

        f, t, s = signal.spectrogram(x=self.signal, fs=self.frequency,
                                     window=self._window_kaiser,
                                     nfft=self._nfft_window_size,
                                     noverlap=self._noverlap_size)

        # correction time
        t = t + self.time_start
        min_frequency, max_frequency = self.freq_limits
        # amplitudes selection
        ds = s[((min_frequency <= f)*(f <= max_frequency))]

        # frequencies selection
        df = f[((min_frequency <= f)*(f <= max_frequency))]
        self._sp_data = SpData(t, df, ds)

    def _scale_limits(self) -> tuple:
        """
        Method for defining spectrogram scale limits
        :return: scale limits
        """
        mid_amp = abs(self._sp_data.amplitudes).mean()
        # dispersion sum for each time interval
        disp_sum = 0
        for i in range(self._sp_data.amplitudes.shape[1]):
            d = np.std(abs(self._sp_data.amplitudes[:, i]) - mid_amp)
            disp_sum += d
        # average dispersion value
        disp_average = disp_sum / self._sp_data.amplitudes.shape[1]

        # minimal scale value (dB)
        bmin = 20 * np.log10(abs(np.min(self._sp_data.amplitudes)))
        # maximal scale value (dB)
        bmax = 20 * np.log10(mid_amp + 9 * disp_average)
        return bmin, bmax

    def _get_scale(self) -> tuple:
        """
        Method for getting scale parameters (matplotlib)
        :return: colormap parameters
        """
        b_min, b_max = self._scale_limits()
        levels = MaxNLocator(nbins=100).tick_values(b_min, b_max)
        color_map = plt.get_cmap('jet')
        norm = BoundaryNorm(boundaries=levels, ncolors=color_map.N,
                            clip=False)
        return color_map, norm

    def _plot(self, output_folder, output_name):
        """
        Method for spectrogram export to png file
        :param output_folder: output folder
        :param output_name: output file name
        """
        warnings.filterwarnings("ignore")
        plt.switch_backend('SVG')

        # document field offset
        mpl.rcParams['figure.subplot.left'] = 0.07
        mpl.rcParams['figure.subplot.right'] = 0.97
        mpl.rcParams['figure.subplot.bottom'] = 0.05
        mpl.rcParams['figure.subplot.top'] = 0.95

        # calc document size in inches (depend on time duration)
        duration = self._sp_data.times[-1] - self._sp_data.times[0]
        if duration > self.max_time_length_sec:
            lx = duration / self.max_time_length_sec * self.spectrogram_size_x_inch
        else:
            lx = self.spectrogram_size_x_inch

        fig, axes = plt.subplots(1, 1)
        fig.set_size_inches(lx, self.spectrogram_size_y_inch)
        fig.dpi = 96

        # calc decibels values
        times, freqs = self._sp_data.times, self._sp_data.frequencies
        amplitudes = 20 * np.log10(abs(self._sp_data.amplitudes))

        c_map, c_norm = self._get_scale()
        axes.pcolormesh(times, freqs, amplitudes, cmap=c_map, norm=c_norm)

        x_label = 'Time, s'
        y_label = 'Frequency, Hz'
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)

        axes.set_title(output_name, fontsize=10)

        export_path = os.path.join(output_folder, output_name + '.png')
        plt.savefig(export_path, dpi=96)
        plt.close(fig)

    def save_spectrogram(self, output_folder, output_name):
        """
        Simple method for creating and exporting spectrogram to png file
        :param output_folder: export folder path
        :param output_name: output file name (without extension)
        """
        self._spectrogram_calc()
        self._plot(output_folder, output_name)
