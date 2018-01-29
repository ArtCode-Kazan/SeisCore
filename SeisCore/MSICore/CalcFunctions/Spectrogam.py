from scipy import signal
import numpy as np


def specgram(time_start, signal_data, frequency_of_signal, nfft_window_size,
             noverlap_size, min_frequency, max_frequency):
    """
    Функция для вычисления параметров 2D-спектрограммы
    :param time_start: разница времени в секундах между временем старта
    прибора и временем начала генерации спектрограммы
    :param signal_data: массив numpy сигнала
    :param frequency_of_signal: частота дискретизации сигнала
    :param nfft_window_size: окно построения спектрограммы
    :param noverlap_size: сдвиг окна
    :param min_frequency: минимальная частота для вычисления спектрограммы
    :param max_frequency: максимальная частота для вычисления спектрограммы
    :return: список вида: [время (с), частота(Гц), амплитуда(усл. единицы)]
    """
    # создание окна Кайзера с параметрами:
    # M=2048 beta=5 sym=false
    window_kaiser = signal.kaiser(2048, 5, False)

    # получение данных спектрограммы
    f, t, S = signal.spectrogram(x=signal_data,
                                 fs=frequency_of_signal,
                                 window=window_kaiser,
                                 nfft=nfft_window_size,
                                 noverlap=noverlap_size)

    # приведение времени к времени старта прибора (секунды)
    t = t + time_start
    # получение массива индексов массива S, элементы которого относятся
    # к интервалу частот
    # [min_frequency<=f<=max_frequency]
    indexs = np.where((min_frequency <= f) & (f <= max_frequency))
    min_index = np.min(indexs)
    max_index = np.max(indexs)

    # получение подмассива dS из массива S, элементы которого лежат
    # в пределах частот
    # [min_frequency<=f<=max_frequency]
    dS = S[min_index:max_index + 1, :]

    # получение подмассива df из массива f, элементы которого лежат в пределах
    # [min_frequency<=f<=max_frequency]
    df = f[indexs]

    # возврат результата
    return [t, df, dS]
