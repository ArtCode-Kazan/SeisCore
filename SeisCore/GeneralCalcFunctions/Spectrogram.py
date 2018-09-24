from scipy import signal
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import warnings
import os


def _specgram_old_(time_start, signal_data, frequency_of_signal,
                   min_frequency=None, max_frequency=None):
    """
    УСТАРЕЛА!!!
    Функция для вычисления параметров 2D-спектрограммы
    :param time_start: разница времени в секундах между временем старта
    прибора и временем начала генерации спектрограммы
    :param signal_data: массив numpy сигнала
    :param frequency_of_signal: частота дискретизации сигнала
    :param min_frequency: минимальная частота для вычисления спектрограммы
    :param max_frequency: максимальная частота для вычисления спектрограммы
    :return: список вида: [время (с), частота(Гц), амплитуда(усл. единицы)]
    """
    # создание окна Кайзера с параметрами:
    # M=2048 beta=5 sym=false
    window_kaiser = signal.windows.kaiser(2048, 5, False)

    # окно построения спектрограммы
    nfft_window_size = 8192
    # сдвиг окна построения спектрограммы
    noverlap_size = 256

    # получение данных спектрограммы
    f, t, s = signal.spectrogram(x=signal_data,
                                 fs=frequency_of_signal,
                                 window=window_kaiser,
                                 nfft=nfft_window_size,
                                 noverlap=noverlap_size)

    # приведение времени к времени старта прибора (секунды)
    t = t + time_start
    # получение массива индексов массива S, элементы которого относятся
    # к интервалу частот
    # [min_frequency<=f<=max_frequency]
    if min_frequency is None and max_frequency is None:
        min_index = 0
        max_index = f.shape[0] - 1
    elif min_frequency is not None and max_frequency is None:
        indexes = np.where(min_frequency <= f)
        min_index = np.min(indexes)
        max_index = np.max(indexes)
    elif min_frequency is None and max_frequency is not None:
        indexes = np.where(f <= max_frequency)
        min_index = np.min(indexes)
        max_index = np.max(indexes)
    else:
        indexes = np.where((min_frequency <= f) & (f <= max_frequency))
        min_index = np.min(indexes)
        max_index = np.max(indexes)

    # получение подмассива dS из массива S, элементы которого лежат
    # в пределах частот
    # [min_frequency<=f<=max_frequency]
    ds = s[min_index:max_index + 1, :]

    # получение подмассива df из массива f, элементы которого лежат в пределах
    # [min_frequency<=f<=max_frequency]
    df = f[min_index:max_index + 1]

    # возврат результата
    return t, df, ds


def _specgram(signal_data, frequency_of_signal, time_start=0,
              max_frequency=None):
    """
    Метод для вычисления данных спектрограммы (переписан с matlab-функции)
    :param signal_data: одномерный массив сигнала
    :param frequency_of_signal: частота сигнала
    :param time_start: время старта сигнала (секунды)
    :param max_frequency: максимальная частота визализации
    :return:
    """
    # создание окна Кайзера с параметрами:
    # M=2048 beta=5 sym=false
    window_kaiser = signal.windows.kaiser(2048, 5, False)

    # сдвиг окна Кайзера
    noverlap_size = 256

    # окно fft-преобразования
    nfft_window_size = 4096

    signal_length = signal_data.shape[0]
    kaiser_size = window_kaiser.shape[0]

    if signal_data.shape[0] < kaiser_size:
        zero_vector = np.zeros(shape=kaiser_size - signal_length,
                               dtype=np.int32)
        signal_data = np.append(signal_data, zero_vector)
        signal_length = kaiser_size

    # подсчет количества передвижек окна
    windows_count = (signal_length - kaiser_size) // noverlap_size + 1

    # создание массива для сохранения данных fft-преобразования каждого окна
    window_data = np.empty(shape=(2 * kaiser_size, windows_count),
                           dtype=complex)

    # процесс расчета идет по каждому окну
    for i in range(windows_count):
        # левая граница окна (включительно, нумерация от нуля)
        left_edge = i * noverlap_size
        # правая граница окна (включительно, нумерация от нуля)
        right_edge = left_edge + kaiser_size

        # выборка сигнала
        selected_signal = signal_data[left_edge:right_edge]
        # умножение выборки сигшнала на окно кайзера
        kaiser_transform = selected_signal * window_kaiser
        # fft-трансформация
        fft_tansform = np.fft.fft(a=kaiser_transform, n=nfft_window_size)
        window_data[:, i] = fft_tansform

    # вычисление предела выборки амплитуд
    if max_frequency is None:
        max_frequency = frequency_of_signal
    edge_lim = int(
        nfft_window_size * max_frequency / frequency_of_signal + 1)

    # получение среза fft-разложения
    window_data = window_data[:edge_lim]

    t = time_start + np.arange(start=0, stop=windows_count * noverlap_size,
                               step=noverlap_size) / frequency_of_signal
    f = np.arange(start=0, stop=edge_lim,
                  step=1) * frequency_of_signal / nfft_window_size
    amplitudes = np.abs(window_data)
    return t, f, amplitudes


def _scale(amplitudes):
    """
    Функция для расчета параметров раскраски цветовой шкалы
    :param amplitudes: матрица значений амплитуд (в усл. ед)
    :return: цветовая шкала cmap, уровни цветовой шкалы norm
    """
    # расчет параметров для раскраски спектрограммы
    # среднее значение амплитуды из выборки по частоте
    mid_amp = abs(amplitudes).mean()
    disp_sum = 0  # сумма дисперсий для каждого интервала времени
    for i in range(amplitudes.shape[1]):
        d = np.std(abs(amplitudes[:, i]) - mid_amp)
        disp_sum += d
    # среднее значение дисперсии за все времена
    disp_average = disp_sum / amplitudes.shape[1]

    # минимальное значение цветовой шкалы (в децибелах!)
    bmin = 20 * np.log10(abs(np.min(amplitudes)))
    # максимальное значение цветовой шкалы (в децибелах!)
    bmax = 20 * np.log10(mid_amp + 9 * disp_average)

    # расчет параметров цветовой шкалы
    # создание уровней
    levels = MaxNLocator(nbins=100).tick_values(bmin, bmax)
    cmap = plt.get_cmap('jet')  # цветовая шкала jet
    # построение цветовой шкалы с учетом уровней
    norm = BoundaryNorm(boundaries=levels, ncolors=cmap.N, clip=False)
    return cmap, norm


def _plot(label, times, frequencies, amplitudes, cmap, norm, output_folder,
         output_name):
    """
    Функция для визуализации данных спектрограммы в виде png-файла
    :param label: название спектрограммы (будет отображено)
    :param times: массив времен
    :param frequencies: массив частот
    :param amplitudes: матрица амплитуд (в усл. единицах!)
    :param cmap: цветовая шкала cmap
    :param norm: уровни цветовой шкалы norm
    :param output_folder: папка, куда будет сохранятся рисунок спектрограммы
    :param output_name: имя выходного файла спектрограмма
    :return: функция ничего не возвращает, работает как процедура

    """
    warnings.filterwarnings("ignore")
    # настройка вывода спектрограммы
    mpl.rcParams['figure.figsize'] = (12, 9)  # размер поля для вывода графика
    mpl.rcParams['figure.dpi'] = 96  # разрешение отображения графика
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    plt.subplot(111)  # подготовка плота
    # отображение спектрограммы в виде децибелов=20*lg(|amp|)
    plt.pcolormesh(times, frequencies, 20 * np.log10(abs(amplitudes)),
                   cmap=cmap, norm=norm)

    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Частота, Гц'
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    # подпись графика
    plt.title(label, fontsize=10)

    # сохранение графика в png
    export_path = os.path.join(output_folder,output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # очистка плота для построения нового графика
    plt.gcf().clear()

    # проверка сохранения файла
    if os.path.isfile(export_path):
        return True
    else:
        return False


def create_spectrogram(signal_data, frequency, max_frequency, label,
                       output_folder,
                       output_name,
                       time_start=0):
    # вычисление парамтеров спектрограммы
    t, f, amplitudes = _specgram(signal_data, frequency, time_start,
                                 max_frequency)

    # определение параметров раскраски шкалы
    cmap, norm = _scale(amplitudes)

    # экспорт спектрограммы в виде файла
    result = _plot(label, times=t, frequencies=f, amplitudes=amplitudes,
                   cmap=cmap, norm=norm, output_folder=output_folder,
                   output_name=output_name)
    return result




