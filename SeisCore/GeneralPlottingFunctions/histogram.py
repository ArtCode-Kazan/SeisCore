import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def histogram(data,bin_size,histo_label):
    """
    Функция построения гистограммы
    :param data: одномерный массив numpy с числовым рядом
    :param bin_size: размер бина
    :param histo_label: название (подпись) гистограммы
    :return: None
    """
    # расчет количества бинов
    bin_count=int((np.max(data)-np.min(data))//bin_size)
    # бинирование данных
    hist, bins = np.histogram(data, bins=bin_count)

    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.97
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    # создание бланка графика
    fig = plt.figure()

    # размер плота в дюймах
    fig.set_size_inches(7, 5)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # расстановка делений по оси x
    # значение одного интервала равно размеру бина
    axes.xaxis.set_major_locator(ticker.MultipleLocator(bin_size))
    # планируется 10 интервалов
    dy_size=np.max(hist)/10
    axes.yaxis.set_major_locator(ticker.MultipleLocator(dy_size))

    # расчет ширины столбца
    width = 1 * (bins[1] - bins[0])
    # расчет положения столбца по x
    center = (bins[:-1] + bins[1:]) / 2
    # построение гистограммы
    axes.bar(center, hist, align='center', width=width,edgecolor= 'black')
    # подпись гистограммы
    axes.set_title(histo_label)
    # отображение гистограммы
    plt.show()

