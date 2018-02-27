from scipy.fftpack import rfft, irfft, fftfreq


def band_pass_filter(signal, frequency, f_min, f_max):
    """
    Функция для полосовой фильтрации
    :param signal: входной одномерный numpy массив сигнала
    :param frequency: частота дискретизации сигнала
    :param f_min: минимальная частота фильтрации
    :param f_max: максимальная частота фильтрации
    :return: отфильтрованный сигнал (одномерный numpy массив)
    """
    # построение частотного ряда
    frequency_array = fftfreq(n=signal.shape[0], d=1.0 / frequency)
    # прямое преобразование Фурье
    f_signal = rfft(signal)
    # зануление амплитуд, частоты которых меньше f_min
    f_signal[(frequency_array < f_min)] = 0
    # зануление амплитуд, частоты которых больше f_max
    f_signal[(frequency_array > f_max)] = 0
    # обратное преобразование Фурье (получится отфильтрованный сигнал)
    filtered_signal = irfft(f_signal)
    return filtered_signal
