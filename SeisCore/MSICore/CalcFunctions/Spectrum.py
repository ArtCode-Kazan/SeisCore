import numpy as np
from numpy.fft import rfft, rfftfreq

"""
Модуль для вычисления 1D-спектра сигнала
"""
# функция получения спектра сигнала
# входные параметры:
# signal - входной сигнал
# frequency - частота дискретизации сигнала
def spectrum(signal, frequency):
    """
    функция получения спектра сигнала
    :param signal: входной сигнал
    :param frequency: частота дискретизации сигнала
    :return: массив numpy спектра (частота, амплитуда)

    """
    # получение количества отсчетов в сигнале
    signal_count = signal.shape[0]
    # быcтрое преобразование фурье
    spectrum_data = rfft(signal)
    # создание пустого массива, который будет в качестве выходных данных
    res = np.empty((signal_count // 2 + 1, 2), dtype=np.float)
    res[:, 0] = rfftfreq(signal_count, 1. / frequency)  # присвоение частот
    res[:, 1] = 2 * abs(spectrum_data) / signal_count  # присвоение амплитуд
    # амплитуды удваиваются, чтобы не потерять энергию
    # (спектр в отрицательных частотах зеркальный)
    return res
