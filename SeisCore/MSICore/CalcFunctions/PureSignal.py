import numpy as np
import sys

from SeisCore.MSICore.CalcFunctions.Spectrum import spectrum
from SeisCore.GeneralCalcFunctions.NormingSignal import norming_signal

"""
Модуль для получения пределов участка сигнала

"""


def pure_signal(signal, sensor_coeff, registrator_coeff, frequency, window,
                overlap, clipping_before, clipping_after, f_min, f_max, df):
    """
    Функция для получения чистого куска сигнала в виде номера отсчета левой
    границы( включительно) и правой границы(включительно)
    :param signal: входной сигнал (исходный сигнал без нормировки)
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
        clipping_before_count = signal.shape[0] * clipping_before // 100
    else:
        clipping_before_count = 0

    # количество отсчетов, удаляемых от конца записи сигнала
    if clipping_after is not None:
        clipping_after_count = signal.shape[0] * clipping_after // 100
    else:
        clipping_after_count = 1
    # отобранный сигнал (после обрезки начала и конца)
    signal_reject = signal[clipping_before_count:-clipping_after_count]

    # подсчет количества интервалов частот
    f = np.arange(start=f_min, stop=f_max + df, step=df, dtype=float)
    f_intervals_count = f.shape[0] - 1

    # подсчет количества окон
    windows_count = (signal_reject.shape[0] - window) // overlap + 1

    # Создание пустой матрицы для помещения результатов вычислений
    result_matrix = np.empty((f_intervals_count + 1, windows_count),
                             dtype=np.float32)

    # процесс расчета идет по каждому окну
    for i in range(windows_count):
        # левая граница окна (включительно, нумерация от 1)
        left_edge = i * overlap + 1
        # правая граница окна (включительно, нумерация от 1)
        right_edge = left_edge + window - 1

        # выборка сигнала
        part_of_signal = signal_reject[left_edge - 1:right_edge].copy()
        # смена типа массива, чтобы можно было провести нормировку
        # (иначе будут нули, так как исходный формат int32)
        part_of_signal = part_of_signal.astype(np.float32)

        # нормировка выборки сигнала
        # нормировка выполняется только внутри окон, так как в случае большой
        # длины массива не хватает памятия для типа np.float32
        part_of_signal = norming_signal(
            signal=part_of_signal,
            sensor_coefficient=sensor_coeff,
            registrator_coefficient=registrator_coeff)

        # Вычисление STD куска сигнала по каждой компоненте
        std = np.std(part_of_signal)

        # добавление коэ-та STD в матрицу result_matrix
        result_matrix[0, i] = std

        # получение спектра куска сигнала
        spectrum_data = spectrum(signal=part_of_signal,
                                 frequency=frequency)

        # суммирование квадратов амплитуд спектра каждой компоненты
        # в заданном интервале частот
        for freq_interval in range(f_intervals_count):
            f1 = f[freq_interval]
            f2 = f[freq_interval + 1]
            # получение индексов элементов спектра, частоты которых
            # укладываются в заданный интервал
            indexes = np.where((spectrum_data[:, 0] >= f1) &
                               (spectrum_data[:, 0] <= f2))

            # получение амплитуд для выбранного окошка частот
            amplitudes = \
                spectrum_data[:, 1][np.min(indexes):np.max(indexes) + 1]

            # возведение амплитуд в квадрат
            amplitudes = amplitudes ** 2

            # сумма квадратов амплитуд
            amp_sum = np.sum(amplitudes)

            # присвоение значения в результирующую матрицу
            result_matrix[freq_interval + 1, i] = amp_sum
        sys.stdout.write(
            '\rОкно {} из {} обработано'.format(i + 1, windows_count))
        sys.stdout.flush()

    # нормировка и суммирование данных ПО ОКНАМ!
    sum_matrix = None
    for j in range(result_matrix.shape[0]):
        result_matrix[j, :] = result_matrix[j, :] / np.max(
            result_matrix[j, :])
        if j == 0:
            sum_matrix = result_matrix[j, :].copy()
        else:
            sum_matrix = sum_matrix + result_matrix[j, :]

    # поиск индекса минимального значения суммы
    # (по сути номер окна (начиная с нуля)
    min_sum_index = np.where(sum_matrix == np.min(sum_matrix))[0]
    # перевод номера окна в пределы отсчетов
    if clipping_before is not None:
        min_number_of_pure_signal = clipping_before_count + min_sum_index \
                                    * overlap + 1
    else:
        min_number_of_pure_signal = min_sum_index * overlap + 1
    max_number_of_pure_signal = min_number_of_pure_signal + window - 1
    return [int(min_number_of_pure_signal), int(max_number_of_pure_signal)]
