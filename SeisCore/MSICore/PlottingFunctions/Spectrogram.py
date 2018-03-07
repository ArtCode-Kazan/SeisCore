import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


def scale(amplitudes):
    """
    Функция для расчета параметров раскраски цветовой шкалы
    :param amplitudes: матрица значений амплитуд (в усл. ед)
    :return: [цветовая шкала cmap, уровни цветовой шкалы norm]
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
    return [cmap, norm]


def plot(label, times, frequencies, amplitudes, cmap, norm, output_folder,
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
    plt.savefig(output_folder + '/' + output_name + '.png', dpi=96)

    # очистка плота для построения нового графика
    plt.gcf().clear()
