from scipy import signal
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import warnings
import os


def _specgram(signal_data, frequency_of_signal,
              min_frequency=None, max_frequency=None, time_start=0):
    """
    Функция вычисления параметров 2D-спектрограммы
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
    # перекрытие окна построения спектрограммы
    noverlap_size = 1792    # 2048-256

    if signal_data.shape[0]<=window_kaiser.shape[0]:
        return None

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
    if min_frequency is None:
        min_frequency = 0
    if max_frequency is None:
        max_frequency = frequency_of_signal/2

    # получение подмассива dS из массива S, элементы которого лежат
    # в пределах частот
    ds = s[((min_frequency <= f) & (f <= max_frequency))]

    # получение подмассива df из массива f, элементы которого лежат в пределах
    # [min_frequency<=f<=max_frequency]
    df = f[((min_frequency <= f) & (f <= max_frequency))]

    # возврат результата
    return t, df, ds


def _scale(amplitudes):
    """
    Функция для расчета параметров раскраски цветовой шкалы
    :param amplitudes: матрица значений амплитуд (комплексные числа)
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


def _plot(times, frequencies, amplitudes, cmap, cnorm,
          output_folder, output_name):
    """
    Функция для визуализации данных спектрограммы в виде png-файла
    :param times: массив времен
    :param frequencies: массив частот
    :param amplitudes: матрица амплитуд (в усл. единицах!)
    :param cmap: цветовая шкала cmap
    :param cnorm: уровни цветовой шкалы norm
    :param output_folder: папка, куда будет сохранятся рисунок спектрограммы
    :param output_name: имя выходного файла спектрограмма
    :return: функция ничего не возвращает, работает как процедура

    """
    warnings.filterwarnings("ignore")
    # настройка вывода спектрограммы
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    # создание бланка графика
    fig = plt.figure()

    # размер плота в дюймах
    ly = 9
    if np.max(times)-np.min(times) > 3600:
        lx = 12 / 3600 * (np.max(times)-np.min(times))
        # ly = 9/20*(max_frequency_visualize-min_frequency_visulize)
    else:
        lx = 12
        # ly = 9
    fig.set_size_inches(lx, ly)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # отображение спектрограммы в виде децибелов=20*lg(|amp|)
    axes.pcolormesh(times, frequencies, 20 * np.log10(abs(amplitudes)),
                    cmap=cmap, norm=cnorm)
    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Частота, Гц'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)
    # подпись графика
    axes.set_title(output_name, fontsize=10)
    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)
    # закрытие плота
    plt.close()

    # проверка сохранения файла
    if os.path.isfile(export_path):
        return True
    else:
        return False


def create_spectrogram(signal_data, frequency, output_folder, output_name,
                       min_frequency=None, max_frequency=None, time_start=0):
    """
    Метод для построения и экспорта спектрограммы в файл
    :param signal_data: сигнал
    :param frequency: частота сигнала
    :param output_folder: папка экспорта
    :param output_name: имя выходного файла (без расширения)
    :param min_frequency: минимальная частота визуализации сигнала
    :param max_frequency: максимальная частота визуализации сигнала
    :param time_start: время от начала записи сигнала (секунды)
    :return:
    """
    # вычисление параметров спектрограммы
    result = _specgram(
        signal_data=signal_data, frequency_of_signal=frequency,
        min_frequency=min_frequency, max_frequency=max_frequency,
        time_start=time_start)

    if result is None:
        return False

    t, f, amplitudes = result

    # определение параметров раскраски шкалы
    cmap, cnorm = _scale(amplitudes)

    # экспорт спектрограммы в виде файла
    result = _plot(times=t, frequencies=f, amplitudes=amplitudes,
                   cmap=cmap, cnorm=cnorm, output_folder=output_folder,
                   output_name=output_name)
    return result
