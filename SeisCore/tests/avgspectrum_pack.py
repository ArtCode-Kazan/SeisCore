# пакетное построение осредненных спектров
import os
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys

from SeisCore.BinaryFile.BinaryFile import BinaryFile
from SeisCore.GeneralCalcFunctions.AverSpectrum import average_spectrum


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



work_directory = r'E:\Lachel\src'
output_folder_name = 'Spectrums'
resample_frequency=250
dt_start=datetime(day=15, month=8, year=2018, hour=0, minute=0, second=0)
dt_stop=datetime(day=16, month=8, year=2018, hour=0, minute=0, second=0)
delta_time=3600*4
window_size=32768
overlap=32768//2
med_filter=7
marmett_filter=7
f_min=1
f_max=30

intervals_count=int((dt_stop-dt_start).total_seconds()/60+1)
folder_struct = os.walk(work_directory)

dt_sum=0
all_intervals_count=0
counter=0
for root, folders, files in folder_struct:
    for file in files:
        name, extension = file.split('.')
        if extension not in ('00', 'xx'):
            continue
        full_path=os.path.join(root,file)

        bin_data = BinaryFile()
        bin_data.path = full_path
        bin_data.record_type='ZXY'
        bin_data.resample_frequency = resample_frequency
        is_correct, errors = bin_data.check_correct()
        if not is_correct:
            continue

        if bin_data.datetime_start<dt_start:
            continue

        for interval in range(intervals_count):
            dt_start_i = dt_start+timedelta(seconds=delta_time*interval)
            dt_stop_i = dt_start_i + timedelta(seconds=delta_time)
            if bin_data.datetime_stop<dt_stop_i:
                break
            all_intervals_count+=1


for root, folders, files in os.walk(work_directory):
    for file in files:
        name, extension = file.split('.')
        if extension not in ('00', 'xx'):
            continue
        full_path=os.path.join(root,file)

        bin_data = BinaryFile()
        bin_data.path = full_path
        bin_data.record_type='ZXY'
        bin_data.resample_frequency = resample_frequency
        is_correct, errors = bin_data.check_correct()
        if not is_correct:
            continue

        if bin_data.datetime_start<dt_start:
            continue

        xi,yi,zi = bin_data.components_index

        for interval in range(intervals_count):
            dt_a_synopsis = datetime.now()
            dt_start_i = dt_start+timedelta(seconds=delta_time*interval)
            dt_stop_i = dt_start_i + timedelta(seconds=delta_time)
            if bin_data.datetime_stop<dt_stop_i:
                break

            bin_data.read_date_time_start = dt_start_i
            bin_data.read_date_time_stop = dt_stop_i
            signal = bin_data.signals
            if signal is None:
                break

            for component in bin_data.record_type:
                signal_i = signal[:, bin_data.record_type.index(component)]

                smooth_avg_sp_data = average_spectrum(
                    signal_i, frequency=resample_frequency,
                    window=window_size, overlap=overlap,
                    med_filter=med_filter, marmett_filter=marmett_filter)

                no_smooth_avg_sp_data = average_spectrum(
                    signal_i, frequency=resample_frequency,
                    window=window_size, overlap=overlap,
                    med_filter=None, marmett_filter=None)

                export_folder=os.path.join(work_directory,
                                           output_folder_name, name, component)
                if not os.path.isdir(export_folder):
                    os.makedirs(export_folder)

                dt_start_label = datetime.strftime(dt_start_i,
                                                   '%Y-%m-%d_%H-%M-%S')
                dt_stop_label = datetime.strftime(dt_stop_i,
                                                  '%Y-%m-%d_%H-%M-%S')
                smooth_file='{}_{}-component_{}-{}.ssc'.format(
                    name, component, dt_start_label, dt_stop_label)
                smooth_path=os.path.join(export_folder, smooth_file)
                no_smooth_file='{}_{}-component_{}-{}.sc'.format(
                    name, component, dt_start_label, dt_stop_label)
                no_smooth_path=os.path.join(export_folder,no_smooth_file)
                pic_name='{}_{}-component_{}-{}'.format(
                    name, component, dt_start_label, dt_stop_label)

                np.savetxt(smooth_path,smooth_avg_sp_data,'%f','\t')
                np.savetxt(no_smooth_path, no_smooth_avg_sp_data, '%f', '\t')
                plot_average_spectrum(frequency=smooth_avg_sp_data[:,0],
                                      spectrum_begin_amplitudes=no_smooth_avg_sp_data[:,1],
                                      spectrum_smooth_amplitudes=smooth_avg_sp_data[:,1],
                                      f_min=f_min, f_max=f_max,
                                      output_folder=export_folder,
                                      output_name=pic_name)
            dt_b_synopsis = datetime.now()

            dt=(dt_b_synopsis-dt_a_synopsis).total_seconds()
            dt_sum+=dt
            counter+=1
            syn_time=dt_sum/counter*(all_intervals_count-counter)/60
            sys.stdout.write('\r Осталось {} минут'.format(int(syn_time)))
            sys.stdout.flush()


