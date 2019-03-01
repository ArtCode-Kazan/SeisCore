import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

from SeisCore.MSICore.CalcFunctions.EnergyCalc import energy_calc


def rgb_for_matlib(rgb):
    """
    Функция преобразования цветов каналов RGB  в hex-формат
    :param rgb: кортеж со значениями каналов RGB
    :return: значение цвета в формате hex
    """
    hex_val = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    return hex_val


def create_spectrograms(data, f_min_visualize, f_max_visualize,
                        amplitude_min_visualize,
                        f_min_spector_visualize, f_max_spector_visualize,
                        f_min_search_amp_max, f_max_search_amp_max, d_freq,
                        d_amp, d_energy, f_min_energy_calc, f_max_energy_calc,
                        energy_zones, energy_zones_colors, energy_gisto_color,
                        is_energy_label,
                        output_files_names, output_folder):
    """
    Функция для построения и сохранения спектров с классификацией энергий
    :param data: входной двухмерный массив numpy,
    в котором первый столбец - частоты, последующие столбцы значения амплитуд
    :param f_min_visualize: минимальная частота для отображения спектра
    :param f_max_visualize: максимальная частота для отображения спектра
    :param amplitude_min_visualize: минимльная амплитуда для отображения
    спектра. Может быть None - по умолчанию ноль
    :param f_min_search_amp_max: минимальная частота для поиска
    максимальной амплитуды спектра
    :param f_max_search_amp_max: максимальная частота для поиска
    максимальной амплитуды спектра
    :param d_freq: шаг сетки графика спектра по частоте
    :param d_amp: шаг сетки графика спектра по амплитуде
    :param d_energy: шаг сетки отображения энергий по энергии
    :param f_min_energy_calc: минимльная частота для расчета энергии
    :param f_max_energy_calc: максимальная частота для расчета энергии
    :param energy_zones: кортеж с границами энергий вида:
    (левая начальная граница, граница1, граница2,..., граница предпоследняя)
    всего допускается 3 ранжирования энергии. Пример: (0, 0.7, 4)
    Первая зона - от 0 до 0.7
    Вторая зона - от 0.7 до 4
    Третья зона - от 4 до максимума энергии
    правая граница последней зоны вычисляется как максимальное значение
    энергии)
    :param energy_zones_colors: кортеж со значениями RGB цветов зон энергий
    вида: ((r1,g1,b1),(r2,g2,b2),..,(rn,gn,bn)).
    всего допускается 3 ранжирования энергии.
    Может быть None - по умолчанию
    (0, 230, 169), (230, 152, 0), (202, 135, 102)
    :param energy_gisto_color: цвет для построения гистограммы значения энергии
    Может быть None - по умолчанию (0, 128, 0)
    :param output_files_names: список с именами выходных файлов спектров в
    порядке следования колонок в массиве data
    :param output_folder: выходная папка для сохранения спектров
    :return:
    """
    # цвета зон энергий по умолчанию
    if energy_zones_colors is None:
        energy_zones_colors = [(0, 230, 169), (230, 152, 0), (202, 135, 102)]

    if amplitude_min_visualize is None:
        amplitude_min_visualize = 0

    if energy_gisto_color is None:
        energy_gisto_color = (0, 128, 0)

    # подсчет количества спектров
    spectors_count = data.shape[1] - 1

    # поиск максимальной амплитуды в заданном интервале частот по всем спектрам
    frequencies = data[:, 0]
    indexes = np.where((frequencies >= f_min_search_amp_max) &
                       (frequencies <= f_max_search_amp_max))
    amp_max = np.max(data[:, 1:][np.min(indexes):np.max(indexes) + 1])

    # вычисление значений энергии в указанном интервале частот
    energy_data = list()
    for i in range(spectors_count):
        frequencies = data[:, 0]
        amplitudes = data[:, i + 1]
        energy = energy_calc(frequencies=frequencies,
                             amplitudes=amplitudes,
                             f_min=f_min_energy_calc,
                             f_max=f_max_energy_calc)
        energy_data.append(energy)

    # вычисление максимальной энергии (чтобы максимум по энергии был немного
    #  внутри графика)
    energy_max = 1.2 * max(energy_data)

    # настройка вывода графика
    mpl.rcParams['figure.figsize'] = (4, 8)  # размер поля для вывода графика
    mpl.rcParams['figure.dpi'] = 70  # разрешение отображения графика
    # настройка шрифта (для отображения русских букв)
    mpl.rc('font', family='Verdana')

    # построение и оформление каждого спектра
    for i in range(spectors_count):
        spector_num = i + 1
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twiny()


        # пределы по осям для отображения гистограмм уровней энергий
        ax1.set_xlim([0, energy_max])
        ax1.set_ylim([f_min_visualize, f_max_visualize])
        # размещение оси сверху
        ax1.xaxis.set_ticks_position("top")

        #  пределы по осям для отображения графика спектра
        ax2.set_xlim([amplitude_min_visualize, amp_max])
        ax2.set_ylim([f_min_visualize, f_max_visualize])
        # размещение оси снизу
        ax2.xaxis.set_ticks_position("bottom")

        # построение классфицированных зон энергий
        for i in range(len(energy_zones)):
            if i != len(energy_zones) - 1:
                # идет построение прямоугольника
                ax1.add_patch(patches.Rectangle(
                    xy=(energy_zones[i], f_min_visualize),
                    width=energy_zones[i + 1] - energy_zones[i],
                    height=f_max_visualize - f_min_visualize,
                    color=rgb_for_matlib(energy_zones_colors[i])))
        else:
            # идет построение последнего прямоугольника
            ax1.add_patch(patches.Rectangle(
                xy=(energy_zones[i], f_min_visualize),
                width=energy_max - energy_zones[i],
                height=f_max_visualize - f_min_visualize,
                color=rgb_for_matlib(energy_zones_colors[i])))

        # построение гистограммы энергии в указанном интервале
        ax1.add_patch(patches.Rectangle(
            xy=(energy_zones[0], f_min_energy_calc),
            width=energy_data[spector_num - 1] - energy_zones[0],
            height=f_max_energy_calc - f_min_energy_calc,
            color=rgb_for_matlib(energy_gisto_color),
            alpha=0.75,
            ec='black',
            lw=1))

        # построение графика спектра
        if f_min_spector_visualize is None:
            f_min_spector_visualize=f_min_visualize
        if f_max_spector_visualize is None:
            f_max_spector_visualize=f_max_visualize

        # получение среза для построения графика спектра
        frequency=data[:, 0]
        amplitudes=data[:, spector_num]
        indexes=np.where((frequency >= f_min_spector_visualize) &
        (frequency <= f_max_spector_visualize))
        min_index=np.min(indexes)
        max_index=np.max(indexes)

        ax2.plot(amplitudes[min_index:max_index+1],
                 frequency[min_index:max_index+1],
                 lw=2,
                 color='#000000')

        # вставка подписи к гистограмме энергии
        if is_energy_label:

            # пределы по осям для отображения надписи знеачения энергии
            # (нужно, так как иначе график спектра будет перекрывать надпись
            # значения энергии)
            ax3 = ax1.twiny()
            ax3.set_xlim([0, energy_max])
            ax3.set_ylim([f_min_visualize, f_max_visualize])
            # отключение видимости осей
            ax3.axis('off')
            x = energy_data[spector_num - 1] - 0.5
            y = (f_max_energy_calc + f_min_energy_calc) / 2

            energy_text = \
                ax3.text(x, y, "{:.2f}".format(energy_data[spector_num - 1]))
            energy_text.set_path_effects(
                [path_effects.Stroke(linewidth=3, foreground='white'),
                path_effects.Normal()])

        # подписи осей
        ax1.set_xlabel(xlabel=u'Энергия, у.е', labelpad=10,
                        color=rgb_for_matlib(energy_gisto_color))
        ax1.tick_params(axis='x', labelcolor=rgb_for_matlib(energy_gisto_color))
        ax1.xaxis.set_label_position('top')
        ax1.set_ylabel(ylabel=u'Частота, Гц', labelpad=0)
        ax2.set_xlabel(xlabel=u'Амплитуда, у.е', labelpad=0)
        ax2.xaxis.set_label_position('bottom')

        # настройка штрихов у осей
        # настройка тиков у шкал спектра
        ax2.xaxis.set_major_locator(
            ticker.MultipleLocator(d_amp))  # разбиение оси х на равные интервалы
        ax2.yaxis.set_major_locator(
            ticker.MultipleLocator(d_freq))  # разбиение оси y на равные интервалы

        # настройка тиков у шкалы x энергии
        ax1.xaxis.set_major_locator(
            ticker.MultipleLocator(d_energy))

        # включение сетки по оси y для спектра
        ax1.yaxis.grid()

        # настройка шрифтов подписей на осях
        ax1.tick_params(axis='both', which='major',
                        labelsize=9)
        ax2.tick_params(axis='both', which='major',
                        labelsize=9)

        plt.savefig(output_folder + '/' + output_files_names[spector_num - 1]
                    + '.png', dpi=200)
        plt.gcf().clear()
        plt.close(fig)


# папка с файлами ssc
spectors_folder = r'D:\TEMP\SibmansExp\nTnWnN_Full\Spectrums'

# расширение файла спектра (без точки)
file_format = 'ssc'
# минимальная частота построения графика
nu_min = 1
# максимальная частота построения графика
nu_max = 10

# минимальная амплитуда
amp_min = 0

# минимальная частота для поиска максимальной амплитуды
nu_min_search_amp = 0
# минимальная частота для поиска максимальной амплитуды
nu_max_search_amp = 5

# шаг сетки по частоте
d_nu = 1
# шаг сетки по амплитуде
d_amp = 1.50846745e-05/10
# шаг сетки по энергии
d_energy = 1.1419510883570183e-06/10

# интервал интегрирования для вычисления энергии
nu_sel_min = 2
nu_sel_max = 3

# границы зон энергий
energy_zones = [0, 1.1419510883570183e-06/2, 1.1419510883570183e-06]

# цвета зон энергий
energy_zones_colors = [(0, 230, 169), (230, 152, 0), (168, 56, 0)]

# цвет гистограммы энергии
energy_gisto_color = '#008000'
# прозрачность гистограммы энергии
energy_gisto_alpha = 0.75

# папка для хранения картинок графиков
pics_folders = spectors_folder + '/Pics_2-3Hz'
if not os.path.exists(pics_folders):
    os.mkdir(pics_folders)

# создание списка с названиями файлов
files_name=list()

for file in os.listdir(spectors_folder):
    if file.endswith('.' + file_format):
        file_name = file[:-len(file_format) - 1]  # имя файла без формата
        files_name.append(file_name)

# подсчет количества строк в файле = числу частот
with open(os.path.join(spectors_folder,files_name[0]+'.'+file_format)) as f:
    freqs_count = sum(1 for _ in f)

files_count = len(files_name)
print('files count = ', files_count ,'freqs_count = ',freqs_count)

# создание пустого массива с общими данными всех файлов
all_data=np.empty((freqs_count,files_count +1), dtype=np.float32)

i=0
for file in os.listdir(spectors_folder):
    if file.endswith('.' + file_format):
        i+=1
        file_name = file[:-len(file_format) - 1]  # имя файла без формата
        current_file = spectors_folder + '/' + file
        # считывание файла в массив
        file_data = np.loadtxt(current_file)
        # заполнение общего массива
        if i==1:
            all_data[:, 0] = file_data[:, 0].copy()
        all_data[:, i] = file_data[:, 1].copy()

        print('read file ' + file_name + ' completed')

create_spectrograms(data=all_data,
                    f_min_visualize=nu_min,
                    f_max_visualize=nu_max,
                    amplitude_min_visualize=0,
                    f_min_spector_visualize=nu_sel_min,
                    f_max_spector_visualize=nu_sel_max,
                    f_min_search_amp_max=nu_min_search_amp,
                    f_max_search_amp_max=nu_max_search_amp,
                    d_freq=d_nu,
                    d_amp=d_amp,
                    d_energy=d_energy,
                    f_min_energy_calc=nu_sel_min,
                    f_max_energy_calc=nu_sel_max,
                    energy_zones=energy_zones,
                    energy_zones_colors=None,
                    energy_gisto_color=None,
                    is_energy_label=True,
                    output_files_names=files_name,
                    output_folder=pics_folders)
