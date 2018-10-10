import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
import os
from SeisCore.GeneralCalcFunctions.Spectrogram import specgram
from SeisCore.GeneralPlottingFunctions.Spectrogram import scale
from SeisCore.BinaryFile.BinaryFile import BinaryFile


def plot_spectrogram(signal, frequency, min_frequency_visulize,
                     max_frequency_visualize, output_folder,
                     output_name, time_start_sec=0):
    """
    Функция для построения 2D спектрограммы в виде картинки
    :param signal: входной сигнал numpy (1D массив)
    :param frequency: частота сигнала, Гц
    :param min_frequency_visulize: минимальная частота для визуализации
    :param max_frequency_visualize: максимальная частота для визуализации
    :param output_folder: папка для экспорта рисунка
    :param output_name: имя файла рисунка (без расширения!)
    :param time_start_sec: время начала куска сигнала (в секундах)
    :return: True, если функция успешно завершена, False, если произошли
    ошибки
    """
    warnings.filterwarnings("ignore")
    # расчет спектрограммы проба расчета, в случае ошибки функция вернет False
    try:
        times, frequencies, amplitudes = specgram(
            time_start=time_start_sec,
            signal_data=signal,
            frequency_of_signal=frequency,
            min_frequency=min_frequency_visulize,
            max_frequency=max_frequency_visualize)
    except ValueError:
        return False

    # расчет параметров шкалы
    cmap, cnorm = scale(amplitudes)

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
    time_duration = signal.shape[0]/frequency
    ly = 9
    if time_duration > 3600:
        lx = 12/3600*time_duration
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
    axes.xaxis.set_major_locator(ticker.MultipleLocator(60*5))
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
    plt.savefig(export_path, dpi=92)
    # закрытие плота
    plt.close()

file_path=r'E:\GRP\PashninskoeDeposit_2018\src\Points_11-20\563_PS16_3292_252\563_PS16_3292_252_180804.00'

bin_data=BinaryFile()
bin_data.path = file_path
bin_data.record_type='ZXY'
bin_data.resample_frequency=250
signals=bin_data.signals

# file=open(r'G:\Data\Data\2018-12-06\6260_05F_131\6260_05F_131_fr_125.xx','wb')
# b = np.empty(shape=84, dtype=np.int32)
# b.astype(np.int32).tofile(file)
# signals.astype(np.int32).tofile(file)
# file.close()

# file_path = r'G:\Data\Data\2018-12-06\6260_05F_131\6260_05F_131.xx'
# b_data=open(file_path,'rb')
# b_data.seek(336)
# sig_data=b_data.read(1000*12*3600)
# sig_data=np.frombuffer(sig_data,dtype=np.int32)
# sig_data = np.reshape(sig_data,newshape=(sig_data.shape[0]//3,3))
plot_spectrogram(signal=signals[:,0],frequency=bin_data.resample_frequency,
                 min_frequency_visulize=1, max_frequency_visualize=70,
                 output_folder=r'E:\GRP\PashninskoeDeposit_2018\src\Points_11-20\563_PS16_3292_252',
                 output_name='qwerty',time_start_sec=0)