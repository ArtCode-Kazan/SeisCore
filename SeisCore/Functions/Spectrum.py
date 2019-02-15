import numpy as np
from numpy.fft import rfft, rfftfreq
from scipy.signal import medfilt
from SeisCore.Functions.Filter import marmett

"""
Модуль для вычисления 1D-спектров сигнала
"""


def spectrum(signal, frequency):
    """
    функция получения обычного Фурье спектра сигнала
    :param signal: входной сигнал
    :param frequency: частота дискретизации сигнала
    :return: массив numpy спектра (частота, амплитуда)

    """
    # получение количества отсчетов в сигнале
    signal_count = signal.shape[0]
    # быстрое преобразование фурье
    spectrum_data = rfft(signal)
    # создание пустого массива, который будет в качестве выходных данных
    res = np.empty((signal_count // 2 + 1, 2), dtype=np.float)
    res[:, 0] = rfftfreq(signal_count, 1 / frequency)  # присвоение частот
    res[:, 1] = 2 * abs(spectrum_data) / signal_count  # присвоение амплитуд
    # амплитуды удваиваются, чтобы не потерять энергию
    # (спектр в отрицательных частотах зеркальный)
    return res


def average_spectrum(signal, frequency, window, overlap,
                     med_filter, marmett_filter):
    """
    Функция вычисления кумулятивного(среднего) спектра
    :param signal: входной сигнал
    :param frequency: частота дискретизации сигнала
    :param window: размер окна расчета спектра (в отсчетах)
    :param overlap: размер сдвига окна (в отсчетах)
    :param med_filter: параметр медианного фильтра (может быть None)
    :param marmett_filter: параметр фильтра marmett
    :return: одномерный массив numpy среднего спектра

    """
    # подсчет количества передвижек окна
    windows_count = (signal.shape[0] - window) // overlap + 1

    # Вычисление первой передвижки окна
    left_edge = 0
    right_edge = window
    selection_signal = signal[left_edge:right_edge]
    sum_a = spectrum(selection_signal, frequency)
    sum_a[:, 1] = np.power(sum_a[:, 1], 2)
    # медианная фильтрация амплитуд (если параметр не None)
    if med_filter is not None:
        sum_a[:, 1] = medfilt(sum_a[:, 1], med_filter)

    # процесс расчета остальных передвижек окон
    for i in range(1, windows_count):
        # левая граница окна
        left_edge = i * overlap
        # правая граница окна
        right_edge = left_edge + window
        # выборка сигнала в заданном окне
        selection_signal = signal[left_edge:right_edge]
        # вычисление спектра и одновременное их суммирование
        sp_data = np.power(spectrum(selection_signal, frequency)[:, 1], 2)
        # медианная фильтрация амплитуд (если параметр не None)
        if med_filter is not None:
            sp_data = medfilt(sp_data, med_filter)
        sum_a[:, 1] = sum_a[:, 1] + sp_data

    # получение среднего спектра (амплитуды)
    sum_a[:, 1] = sum_a[:, 1] / windows_count

    # фильтрация marmett амплитуд (если параметр не None)
    if marmett_filter is not None:
        sum_a[:, 1] = marmett(sum_a[:, 1], marmett_filter)

    # возврат кумулятивного (среднего) спектра
    return sum_a
