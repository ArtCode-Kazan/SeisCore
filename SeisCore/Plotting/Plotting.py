import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def plot_signal(time_start_sec, frequency, signal, label, output_folder,
                output_name):
    """
    Функция для построения графика сигнала
    :param time_start_sec: время в секундах, с которого строится сигнал (
    нужен для построения временного ряда)
    :param frequency: частота дискретизации (нужен для построения временного ъ
    ряда)
    :param signal: одномерный массив сигнала
    :param label: заголовок графика
    :param output_folder: папка куда сохраняется график
    :param output_name: имя файла рисунка графика (без расширения)
    :return: None
    """
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
    fig.set_size_inches(13, 10)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # Нормировка амплитуды сигнала на 1000 для удобства отображения
    norm_coeff = 1000
    signal = signal/1000

    # пределы по осям
    # ось x - время в секундах
    t_min = time_start_sec
    t_max = time_start_sec+(signal.shape[0] - 1) / frequency
    axes.set_xlim(t_min, t_max)
    # специальная подпись оси с интервалом 300 секунд
    axes.set_xticks(np.arange(t_min, t_max + 1, 300))

    # ось y - амплитуда сигнала
    amp_min = np.min(signal)
    amp_max = np.max(signal)
    axes.set_ylim(amp_min, amp_max)
    # генерация массива времен
    time_array = np.linspace(start=t_min, stop=t_max, num=signal.shape[0])

    # построение графика
    axes.plot(time_array, signal, lw=0.5, color='#FF0000')

    # заголовки осей
    x_label = u'Время, с'
    y_label = u'Амплитуда, усл. ед, x{}'.format(norm_coeff)
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)
    # подпись графика
    axes.set_title(label, fontsize=10)

    plt.grid()  # включение сетки графика

    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)


def plot_average_spectrum(frequency, spectrum_begin_amplitudes,
                          spectrum_smooth_amplitudes,
                          f_min, f_max,
                          output_folder, output_name):
    """
    Функция для оформления осредненного (кумулятивного) спектра в виде
    png-картинки, на которой отображается исходный средний спектр (без
    сглаживания) и средний спектр с параметрами сглаживания (медианный
    фильтр и (или) фильтр Marmett)
    :param frequency: общий ряд частот как для спектра без сглаживания,
    так и со сглаживанием
    :param spectrum_begin_amplitudes: набор амплитуд изначального среднего
    спектра без сглаживания
    :param spectrum_smooth_amplitudes: набор амплитуд среднего спектра
    после сглаживания
    :param f_min: минимальная частота отображения спектра.
    Может быть None - по умолчанию миниальная частота спектра
    :param f_max: максимальная частота отображения спектра
    Может быть None - по умолчанию максимальная частота спектра
    :param output_folder: выходная папка сохранения спектра
    :param output_name: выходное имя файла картинки спектра
    :return: функция ничего не возвращает. Работает как процедура
    """
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # настройка отступов полей
    mpl.rcParams['figure.subplot.left'] = 0.07
    mpl.rcParams['figure.subplot.right'] = 0.8
    mpl.rcParams['figure.subplot.bottom'] = 0.05
    mpl.rcParams['figure.subplot.top'] = 0.95

    # создание бланка графика
    fig = plt.figure()

    # размер плота в дюймах
    fig.set_size_inches(13, 10)
    # разрешение отображения графика
    fig.dpi = 96
    # подготовка осей
    axes = fig.add_subplot(111)

    # пределы по осям
    if f_min is None:
        f_min = frequency[0]
    if f_max is None:
        f_max = frequency[-1]
    axes.set_xlim(f_min, f_max)

    # получение среза частот в заданном частотном диапазоне визуализации
    selection_frequency = frequency[
        (frequency >= f_min) * (frequency <= f_max)]

    # получение срезов массивов амплитуд в заданном частотном диаппазоне
    selection_spectrum_begin_amplitudes = \
        spectrum_begin_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    selection_spectrum_smooth_amplitudes = \
        spectrum_smooth_amplitudes[(frequency >= f_min) * (frequency <= f_max)]

    # поиск максимальной и минимальной амплитуды в выборках
    amp_min = np.min([np.min(selection_spectrum_begin_amplitudes),
                      np.min(selection_spectrum_smooth_amplitudes)])
    amp_max = np.max([np.max(selection_spectrum_begin_amplitudes),
                      np.max(selection_spectrum_smooth_amplitudes)])
    axes.set_ylim(amp_min, amp_max)

    # построение графика исходного, несглаженного спектра (толщина линии 1)
    axes.plot(selection_frequency, selection_spectrum_begin_amplitudes,
              lw=1, color='#000000',
              label=u'Кумулятивный спектр\n(без сглаживания))')

    axes.plot(selection_frequency, selection_spectrum_smooth_amplitudes,
              lw=2, color='#FF0000',
              label=u'Кумулятивный спектр\n(со сглаживанием)')

    axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # заголовки осей
    x_label = u'Частота, Гц'
    y_label = u'Амплитуда, усл. ед'
    axes.set_ylabel(y_label)
    axes.set_xlabel(x_label)
    # подпись графика
    axes.set_title(output_name, fontsize=10)

    axes.grid()  # включение сетки графика

    # сохранение графика в png
    export_path = os.path.join(output_folder, output_name + '.png')
    plt.savefig(export_path, dpi=96)

    # закрытие плота
    plt.close(fig)
