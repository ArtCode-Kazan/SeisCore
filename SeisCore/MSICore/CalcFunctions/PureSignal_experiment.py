<<<<<<< HEAD
import numpy as np
import sys

from SeisCore.MSICore.CalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.NormingSignal import norming_signal

"""
Модуль для получения пределов участка сигнала (ЭКСПЕРИМЕНТАЛЬНЫЙ МОДУЛЬ)

"""


def pure_signal(signal_x, signal_y, signal_z, sensor_coeff, registrator_coeff,
                frequency, window, overlap, f_min, f_max, df,
                clipping_before=None, clipping_after=None):
    """
    Функция для получения чистого куска сигнала в виде номера отсчета левой
    границы( включительно) и правой границы(включительно)
    :param signal_x: входной сигнал x-компоненты (исходный сигнал без
    нормировки)
    :param signal_y: входной сигнал y-компоненты (исходный сигнал без
    нормировки)
    :param signal_z: входной сигнал z-компоненты (исходный сигнал без
    нормировки)
    :param sensor_coeff: калибровочный коэф-т сенсора
    :param registrator_coeff: калибровочный коэф-т регистратора
    :param frequency: частота дискретизации
    :param window: окно выделения "чистого" сигнала
    :param overlap: сдвиг окна выделения "чистого" сигнала
    :param clipping_before: процент отсчетов от всего сигнала,
    которые будут исключены от начала записи сигнала при расчете
    :param clipping_after: процент отсчетов от всего сигнала,
    которые будут исключены от конца записи сигнала при расчете
    :param f_min: минимальная частота для анализа
    :param f_max: максимальная частота для анализа
    :param df: шаг разбиения интервала частот
    :return: список в виде [левая граница( включительно),
    правая граница(включительно) чистого участка сигнала]

    """
    # обрезка с начала и конца сигнала на нужный процент

    # количество отсчетов, удаляемых от начала записи сигнала
    if clipping_before is not None:
        clipping_before_count = signal_x.shape[0] * clipping_before // 100
    else:
        clipping_before_count = 0

    # количество отсчетов, удаляемых от конца записи сигнала
    if clipping_after is not None:
        clipping_after_count = signal_x.shape[0] * clipping_after // 100
    else:
        clipping_after_count = 1
    # отобранный сигнал (после обрезки начала и конца)
    signal_x_reject = signal_x[clipping_before_count:-clipping_after_count]
    signal_y_reject = signal_y[clipping_before_count:-clipping_after_count]
    signal_z_reject = signal_z[clipping_before_count:-clipping_after_count]

    # подсчет количества интервалов частот
    f = np.arange(start=f_min, stop=f_max + df, step=df, dtype=float)
    f_intervals_count = f.shape[0] - 1

    # подсчет количества окон
    windows_count = (signal_x_reject.shape[0] - window) // overlap + 1

    # Создание пустой матрицы для помещения результатов вычислений
    result_matrix = np.empty((3, f_intervals_count + 1, windows_count),
                             dtype=np.float32)

    # процесс расчета идет по каждому окну
    for i in range(windows_count):
        # левая граница окна (включительно, нумерация от 1)
        left_edge = i * overlap + 1
        # правая граница окна (включительно, нумерация от 1)
        right_edge = left_edge + window - 1

        # выборка сигнала
        # смена типа массива, чтобы можно было провести нормировку
        # (иначе будут нули, так как исходный формат int32)
        part_of_signal_x = signal_x_reject[left_edge - 1:right_edge].astype(
            np.float32)
        part_of_signal_y = signal_y_reject[left_edge - 1:right_edge].astype(
            np.float32)
        part_of_signal_z = signal_z_reject[left_edge - 1:right_edge].astype(
            np.float32)

        # нормировка выборки сигнала
        # нормировка выполняется только внутри окон, так как в случае большой
        # длины массива не хватает памятия для типа np.float32
        part_of_signal_x = norming_signal(
            signal=part_of_signal_x,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)
        part_of_signal_y = norming_signal(
            signal=part_of_signal_y,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)
        part_of_signal_z = norming_signal(
            signal=part_of_signal_z,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)

        # Вычисление STD куска сигнала по каждой компоненте
        std_x = np.std(part_of_signal_x)
        std_y = np.std(part_of_signal_y)
        std_z = np.std(part_of_signal_z)

        # добавление коэ-та STD в матрицу result_matrix
        result_matrix[0, 0, i] = std_x
        result_matrix[1, 0, i] = std_y
        result_matrix[2, 0, i] = std_z

        # получение спектра куска сигнала
        spectrum_data_x = spectrum(signal=part_of_signal_x,
                                   frequency=frequency)
        spectrum_data_y = spectrum(signal=part_of_signal_y,
                                   frequency=frequency)
        spectrum_data_z = spectrum(signal=part_of_signal_z,
                                   frequency=frequency)
        # суммирование квадратов амплитуд спектра каждой компоненты
        # в заданном интервале частот
        for freq_interval in range(f_intervals_count):
            f1 = f[freq_interval]
            f2 = f[freq_interval + 1]
            # получение индексов элементов спектра, частоты которых
            # укладываются в заданный интервал
            amplitudes_x = spectrum_data_x[(
                    (spectrum_data_x[:, 0] >= f1) &
                    (spectrum_data_x[:, 0] <= f2))][:, 1]
            amplitudes_y = spectrum_data_y[(
                    (spectrum_data_y[:, 0] >= f1) &
                    (spectrum_data_y[:, 0] <= f2))][:, 1]
            amplitudes_z = spectrum_data_z[(
                    (spectrum_data_z[:, 0] >= f1) &
                    (spectrum_data_z[:, 0] <= f2))][:, 1]

            # возведение амплитуд в квадрат
            amplitudes_x = amplitudes_x ** 2
            amplitudes_y = amplitudes_y ** 2
            amplitudes_z = amplitudes_z ** 2

            # сумма квадратов амплитуд
            amp_sum_x = np.sum(amplitudes_x)
            amp_sum_y = np.sum(amplitudes_y)
            amp_sum_z = np.sum(amplitudes_z)

            # присвоение значения в результирующую матрицу
            result_matrix[0, freq_interval + 1, i] = amp_sum_x
            result_matrix[1, freq_interval + 1, i] = amp_sum_y
            result_matrix[2, freq_interval + 1, i] = amp_sum_z

        sys.stdout.write(
            '\rОкно {} из {} обработано'.format(i + 1, windows_count))
        sys.stdout.flush()

    # нормировка и суммирование данных ПО ОКНАМ!
    sum_matrix_x = None
    sum_matrix_y = None
    sum_matrix_z = None
    for j in range(result_matrix.shape[1]):
        result_matrix[0, j, :] = result_matrix[0, j, :] / np.max(
            result_matrix[0, j, :])
        result_matrix[1, j, :] = result_matrix[1, j, :] / np.max(
            result_matrix[1, j, :])
        result_matrix[2, j, :] = result_matrix[2, j, :] / np.max(
            result_matrix[2, j, :])

        if j == 0:
            sum_matrix_x = result_matrix[0, j, :]
            sum_matrix_y = result_matrix[1, j, :]
            sum_matrix_z = result_matrix[2, j, :]
        else:
            sum_matrix_x = sum_matrix_x + result_matrix[0, j, :]
            sum_matrix_y = sum_matrix_y + result_matrix[1, j, :]
            sum_matrix_z = sum_matrix_z + result_matrix[2, j, :]

    test_matrix = sum_matrix_z / (
                (sum_matrix_x ** 2 + sum_matrix_y ** 2) ** 0.5)

    # поиск индекса минимального значения суммы
    # (по сути номер окна (начиная с нуля)
    min_test_index = np.where(test_matrix == np.min(test_matrix))[0]
    # перевод номера окна в пределы отсчетов
    if clipping_before is not None:
        min_number_of_pure_signal = \
            int(clipping_before_count + min_test_index * overlap + 1)
    else:
        min_number_of_pure_signal = int(min_test_index * overlap + 1)
    max_number_of_pure_signal = min_number_of_pure_signal + window - 1

    write_array = np.empty((window, 2), dtype=np.int32)
    write_array[:, 0] = np.arange(min_number_of_pure_signal,
                                  max_number_of_pure_signal + 1, 1)

    write_array[:, 1] = signal_x[min_number_of_pure_signal:max_number_of_pure_signal+1]
    np.savetxt('D:/TEMP/signal_x_experiment.dat', write_array)

    write_array[:, 1] = signal_y[min_number_of_pure_signal:max_number_of_pure_signal + 1]
    np.savetxt('D:/TEMP/signal_y_experiment.dat', write_array)

    write_array[:, 1] = signal_z[min_number_of_pure_signal:max_number_of_pure_signal + 1]
    np.savetxt('D:/TEMP/signal_z_experiment.dat', write_array)
    return [int(min_number_of_pure_signal), int(max_number_of_pure_signal)]
=======
import numpy as np
import sys

from SeisCore.MSICore.CalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.NormingSignal import norming_signal

"""
Модуль для получения пределов участка сигнала (ЭКСПЕРИМЕНТАЛЬНЫЙ МОДУЛЬ)

"""


def pure_signal(signal_x, signal_y, signal_z, sensor_coeff, registrator_coeff,
                frequency, window, overlap, f_min, f_max, df,
                clipping_before=None, clipping_after=None):
    """
    Функция для получения чистого куска сигнала в виде номера отсчета левой
    границы( включительно) и правой границы(включительно)
    :param signal_x: входной сигнал x-компоненты (исходный сигнал без
    нормировки)
    :param signal_y: входной сигнал y-компоненты (исходный сигнал без
    нормировки)
    :param signal_z: входной сигнал z-компоненты (исходный сигнал без
    нормировки)
    :param sensor_coeff: калибровочный коэф-т сенсора
    :param registrator_coeff: калибровочный коэф-т регистратора
    :param frequency: частота дискретизации
    :param window: окно выделения "чистого" сигнала
    :param overlap: сдвиг окна выделения "чистого" сигнала
    :param clipping_before: процент отсчетов от всего сигнала,
    которые будут исключены от начала записи сигнала при расчете
    :param clipping_after: процент отсчетов от всего сигнала,
    которые будут исключены от конца записи сигнала при расчете
    :param f_min: минимальная частота для анализа
    :param f_max: максимальная частота для анализа
    :param df: шаг разбиения интервала частот
    :return: список в виде [левая граница( включительно),
    правая граница(включительно) чистого участка сигнала]

    """
    # обрезка с начала и конца сигнала на нужный процент

    # количество отсчетов, удаляемых от начала записи сигнала
    if clipping_before is not None:
        clipping_before_count = signal_x.shape[0] * clipping_before // 100
    else:
        clipping_before_count = 0

    # количество отсчетов, удаляемых от конца записи сигнала
    if clipping_after is not None:
        clipping_after_count = signal_x.shape[0] * clipping_after // 100
    else:
        clipping_after_count = 1
    # отобранный сигнал (после обрезки начала и конца)
    signal_x_reject = signal_x[clipping_before_count:-clipping_after_count]
    signal_y_reject = signal_y[clipping_before_count:-clipping_after_count]
    signal_z_reject = signal_z[clipping_before_count:-clipping_after_count]

    # подсчет количества интервалов частот
    f = np.arange(start=f_min, stop=f_max + df, step=df, dtype=float)
    f_intervals_count = f.shape[0] - 1

    # подсчет количества окон
    windows_count = (signal_x_reject.shape[0] - window) // overlap + 1

    # Создание пустой матрицы для помещения результатов вычислений
    result_matrix = np.empty((3, f_intervals_count + 1, windows_count),
                             dtype=np.float32)

    # процесс расчета идет по каждому окну
    for i in range(windows_count):
        # левая граница окна (включительно, нумерация от 1)
        left_edge = i * overlap + 1
        # правая граница окна (включительно, нумерация от 1)
        right_edge = left_edge + window - 1

        # выборка сигнала
        # смена типа массива, чтобы можно было провести нормировку
        # (иначе будут нули, так как исходный формат int32)
        part_of_signal_x = signal_x_reject[left_edge - 1:right_edge].astype(
            np.float32)
        part_of_signal_y = signal_y_reject[left_edge - 1:right_edge].astype(
            np.float32)
        part_of_signal_z = signal_z_reject[left_edge - 1:right_edge].astype(
            np.float32)

        # нормировка выборки сигнала
        # нормировка выполняется только внутри окон, так как в случае большой
        # длины массива не хватает памятия для типа np.float32
        part_of_signal_x = norming_signal(
            signal=part_of_signal_x,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)
        part_of_signal_y = norming_signal(
            signal=part_of_signal_y,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)
        part_of_signal_z = norming_signal(
            signal=part_of_signal_z,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)

        # Вычисление STD куска сигнала по каждой компоненте
        std_x = np.std(part_of_signal_x)
        std_y = np.std(part_of_signal_y)
        std_z = np.std(part_of_signal_z)

        # добавление коэ-та STD в матрицу result_matrix
        result_matrix[0, 0, i] = std_x
        result_matrix[1, 0, i] = std_y
        result_matrix[2, 0, i] = std_z

        # получение спектра куска сигнала
        spectrum_data_x = spectrum(signal=part_of_signal_x,
                                   frequency=frequency)
        spectrum_data_y = spectrum(signal=part_of_signal_y,
                                   frequency=frequency)
        spectrum_data_z = spectrum(signal=part_of_signal_z,
                                   frequency=frequency)
        # суммирование квадратов амплитуд спектра каждой компоненты
        # в заданном интервале частот
        for freq_interval in range(f_intervals_count):
            f1 = f[freq_interval]
            f2 = f[freq_interval + 1]
            # получение индексов элементов спектра, частоты которых
            # укладываются в заданный интервал
            amplitudes_x = spectrum_data_x[(
                    (spectrum_data_x[:, 0] >= f1) &
                    (spectrum_data_x[:, 0] <= f2))][:, 1]
            amplitudes_y = spectrum_data_y[(
                    (spectrum_data_y[:, 0] >= f1) &
                    (spectrum_data_y[:, 0] <= f2))][:, 1]
            amplitudes_z = spectrum_data_z[(
                    (spectrum_data_z[:, 0] >= f1) &
                    (spectrum_data_z[:, 0] <= f2))][:, 1]

            # возведение амплитуд в квадрат
            amplitudes_x = amplitudes_x ** 2
            amplitudes_y = amplitudes_y ** 2
            amplitudes_z = amplitudes_z ** 2

            # сумма квадратов амплитуд
            amp_sum_x = np.sum(amplitudes_x)
            amp_sum_y = np.sum(amplitudes_y)
            amp_sum_z = np.sum(amplitudes_z)

            # присвоение значения в результирующую матрицу
            result_matrix[0, freq_interval + 1, i] = amp_sum_x
            result_matrix[1, freq_interval + 1, i] = amp_sum_y
            result_matrix[2, freq_interval + 1, i] = amp_sum_z

        sys.stdout.write(
            '\rОкно {} из {} обработано'.format(i + 1, windows_count))
        sys.stdout.flush()

    # нормировка и суммирование данных ПО ОКНАМ!
    sum_matrix_x = None
    sum_matrix_y = None
    sum_matrix_z = None
    for j in range(result_matrix.shape[1]):
        result_matrix[0, j, :] = result_matrix[0, j, :] / np.max(
            result_matrix[0, j, :])
        result_matrix[1, j, :] = result_matrix[1, j, :] / np.max(
            result_matrix[1, j, :])
        result_matrix[2, j, :] = result_matrix[2, j, :] / np.max(
            result_matrix[2, j, :])

        if j == 0:
            sum_matrix_x = result_matrix[0, j, :]
            sum_matrix_y = result_matrix[1, j, :]
            sum_matrix_z = result_matrix[2, j, :]
        else:
            sum_matrix_x = sum_matrix_x + result_matrix[0, j, :]
            sum_matrix_y = sum_matrix_y + result_matrix[1, j, :]
            sum_matrix_z = sum_matrix_z + result_matrix[2, j, :]

    test_matrix = sum_matrix_z / (
                (sum_matrix_x ** 2 + sum_matrix_y ** 2) ** 0.5)

    # поиск индекса минимального значения суммы
    # (по сути номер окна (начиная с нуля)
    min_test_index = np.where(test_matrix == np.min(test_matrix))[0]
    # перевод номера окна в пределы отсчетов
    if clipping_before is not None:
        min_number_of_pure_signal = \
            int(clipping_before_count + min_test_index * overlap + 1)
    else:
        min_number_of_pure_signal = int(min_test_index * overlap + 1)
    max_number_of_pure_signal = min_number_of_pure_signal + window - 1

    write_array = np.empty((window, 2), dtype=np.int32)
    write_array[:, 0] = np.arange(min_number_of_pure_signal,
                                  max_number_of_pure_signal + 1, 1)

    write_array[:, 1] = signal_x[min_number_of_pure_signal:max_number_of_pure_signal+1]
    np.savetxt('D:/TEMP/signal_x_experiment.dat', write_array)

    write_array[:, 1] = signal_y[min_number_of_pure_signal:max_number_of_pure_signal + 1]
    np.savetxt('D:/TEMP/signal_y_experiment.dat', write_array)

    write_array[:, 1] = signal_z[min_number_of_pure_signal:max_number_of_pure_signal + 1]
    np.savetxt('D:/TEMP/signal_z_experiment.dat', write_array)
    return [int(min_number_of_pure_signal), int(max_number_of_pure_signal)]
>>>>>>> Home
