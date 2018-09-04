from scipy import signal
import numpy as np


def specgram(time_start, signal_data, frequency_of_signal,
             min_frequency=None, max_frequency=None):
    """
    Функция для вычисления параметров 2D-спектрограммы
    :param time_start: разница времени в секундах между временем старта
    прибора и временем начала генерации спектрограммы
    :param signal_data: массив numpy сигнала
    :param frequency_of_signal: частота дискретизации сигнала
    :param min_frequency: минимальная частота для вычисления спектрограммы
    :param max_frequency: максимальная частота для вычисления спектрограммы
    :return: список вида: [время (с), частота(Гц), амплитуда(усл. единицы)]
    """
    # создание окна Кайзера с параметрами:
    # M=2048 beta=5 sym=false
    window_kaiser = signal.windows.kaiser(2048, 5, False)

    # окно построения спектрограммы
    nfft_window_size = 8192
    # сдвиг окна построения спектрограммы
    noverlap_size = 256

    # получение данных спектрограммы
    f, t, s = signal.spectrogram(x=signal_data,
                                 fs=frequency_of_signal,
                                 window=window_kaiser,
                                 nfft=nfft_window_size,
                                 noverlap=noverlap_size)

    # приведение времени к времени старта прибора (секунды)
    t = t + time_start
    # получение массива индексов массива S, элементы которого относятся
    # к интервалу частот
    # [min_frequency<=f<=max_frequency]
    if min_frequency is None and max_frequency is None:
        min_index = 0
        max_index = f.shape[0] - 1
    elif min_frequency is not None and max_frequency is None:
        indexes = np.where(min_frequency <= f)
        min_index = np.min(indexes)
        max_index = np.max(indexes)
    elif min_frequency is None and max_frequency is not None:
        indexes = np.where(f <= max_frequency)
        min_index = np.min(indexes)
        max_index = np.max(indexes)
    else:
        indexes = np.where((min_frequency <= f) & (f <= max_frequency))
        min_index = np.min(indexes)
        max_index = np.max(indexes)

    # получение подмассива dS из массива S, элементы которого лежат
    # в пределах частот
    # [min_frequency<=f<=max_frequency]
    ds = s[min_index:max_index + 1, :]

    # получение подмассива df из массива f, элементы которого лежат в пределах
    # [min_frequency<=f<=max_frequency]
    df = f[min_index:max_index + 1]

    # возврат результата
    return t, df, ds
