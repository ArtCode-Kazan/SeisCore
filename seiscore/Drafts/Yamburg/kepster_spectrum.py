import os

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from seiscore.functions.Spectrum import spectrum
from seiscore.functions.Spectrum import cepstral_spectrum, cepstral_spectrum_from_signal


plt.switch_backend('SVG')


def plot_spectrum(frequency, amplitude, label, output_folder,
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
    # mpl.rc('font', family='Verdana')

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

    # пределы по осям
    # ось x - время в секундах
    f_min = frequency[0]
    f_max = frequency[-1]
    axes.set_xlim(f_min, f_max)

    # ось y - амплитуда сигнала
    amp_min = np.min(amplitude)
    amp_max = np.max(amplitude)
    axes.set_ylim(amp_min, amp_max)

    # построение графика
    axes.plot(frequency, amplitude, lw=0.5, color='#FF0000')

    # заголовки осей
    x_label = 'Время, с'
    y_label = 'Амплитуда, усл. ед'
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


folder=r'/media/michael/Data/Projects/Yamburg/Modeling/EnergyAnalysis/30302'
signal_file='CommonGoodSignal_30302.dat'
file_prefix=''
time_start=0
t0, tn=0.1, 10

signal_data=np.loadtxt(os.path.join(folder, signal_file), skiprows=1,
                       delimiter='\t')
signal_data[:,0]=signal_data[:,0]/1000
signal_data=signal_data[signal_data[:,0]>time_start]
freq=1/(signal_data[1,0]-signal_data[0,0])


si=signal_data[:, 60]

cep_sp=cepstral_spectrum_from_signal(signal=si, frequency=freq,
                                     using_log=False)

np.savetxt(os.path.join(folder,f'{file_prefix}_Component_z.dat'),
       cep_sp, delimiter='\t', header='Time\tAmplitude',
       comments='')
cep_sp=cep_sp[(cep_sp[:,0]>=t0)*(cep_sp[:,0]<=tn)]

# cep_sp=cep_sp[(cep_sp[:,0]>=cep_t_min)*(cep_sp[:,0]<=cep_t_max)]
plot_spectrum(frequency=cep_sp[:,0], amplitude=cep_sp[:,1],
          label=f'{file_prefix}_Component_z',
          output_folder=folder,
          output_name=f'{file_prefix}_Component_z')
