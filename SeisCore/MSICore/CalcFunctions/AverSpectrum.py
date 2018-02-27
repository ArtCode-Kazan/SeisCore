import numpy as np
from scipy.signal import medfilt

from SeisCore.MSICore.CalcFunctions.Spectrum import spectrum


"""
Модуль для расчета осредненнего (кумулятивного спектра)

"""

def marmett(signal, order):
    """
    функция фильтра marmett
    :param signal: входной сигнал
    :param order: порядок фильтра
    :return: отфильтрованный сигнал (длина сигнала равна исходному)
    """
    for i in range(order):
        j = 1
        recalc = signal.copy()
        while j < signal.shape[0] - 1:
            recalc[j] = (signal[j - 1] + signal[j + 1]) / 4 + signal[j] / 2
            j += 1
        recalc[0] = (signal[0] + signal[1]) / 2
        recalc[-1] = (signal[-1] + signal[-2]) / 2
        signal = recalc.copy()
    return signal


def average_spectrum(signal, frequency, window, overlap,
                     med_filtr, marmett_filtr):
    """
    Функция вычисления кумулятивного(среднего) спектра
    :param signal: входной сигнал
    :param frequency: частота дискретизации сигнала
    :param window: размер окна расчета спектра (в отсчетах)
    :param overlap: размер сдвига окна (в отсчетах)
    :param med_filtr: параметр медианного фильтра (может быть None)
    :param marmett_filtr: параметр фильтра marmett
    :return: одномерный массив numpy среднего спектра

    """
    # подсчет количества передвижек окна
    windows_count = (signal.shape[0] - window) // overlap + 1

    # процесс расчета идет по каждому окну
    for i in range(windows_count):
        # левая граница окна (включительно, нумерация от нуля)
        left_edge = i * overlap
        # правая граница окна (включительно, нумерация от нуля)
        right_edge = left_edge + window - 1
        # выборка сигнала в заданном окне
        # right_edge+1, так как в python интервалы полуоткрытые
        selection_signal = signal[left_edge:right_edge + 1]
        # вычисление спектра и одновременное их суммирование
        if i == 0:
            sum_a = spectrum(selection_signal, frequency)
            sum_a[:, 1] = np.power(sum_a[:, 1], 2)
            # медианная фильтрация амплитуд (если параметр не None)
            if med_filtr is not None:
                sum_a[:, 1] = medfilt(sum_a[:, 1], med_filtr)
        else:
            sp_data = np.power(spectrum(selection_signal, frequency)[:, 1], 2)
            # медианная фильтрация амплитуд (если параметр не None)
            if med_filtr is not None:
                sp_data = medfilt(sp_data, med_filtr)
            sum_a[:, 1] = sum_a[:, 1] + sp_data

    # получение среднего спектра (амплитуды)
    sum_a[:, 1] = sum_a[:, 1] / windows_count

    # фильтрация marmett амплитуд (если параметр не None)
    if marmett_filtr is not None:
        sum_a[:, 1] = marmett(sum_a[:, 1], marmett_filtr)

    # возврат кумулятивного (среднего) спектра
    return sum_a
