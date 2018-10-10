import numpy as np
cimport numpy as np


def resampling(np.ndarray[np.int_t, ndim=2] signal,
               int resample_parameter):
    """
    Функция для ресемплирования сигнала
    :param signal: одномерный массив сигнала для ресемплирования
    :param resample_parameter: параметр ресемплирования
    :return: одномерный массив сигнала после ресемплирования
    """

    cdef:
        # Количество дискрет в исходном сигнале
        int discrete_amount
        # Количество дискрет в ресемплированном сигнале
        int resample_discrete_amount
        # Итеративные переменные
        int i, j
        # Вычисление сумм для нахождения среднего
        int sum_a, sum_b, sum_c
        # Вычисленные значения после ресемплирования
        int value_a, value_b, value_c

    # проверка кратности длины сигнала и параметра ресемплирования
    discrete_amount = signal.shape[0]
    if discrete_amount % resample_parameter != 0:
        return None
    # расчет длины ресемплированного сигнала
    resample_discrete_amount = discrete_amount // resample_parameter

    # Создание выходного массива
    cdef:
        np.ndarray[np.int_t, ndim = 2] resample_signal = np.empty(shape=(resample_discrete_amount,3),
                                                                  dtype=np.int32)
    # операция ресемплирования
    for i in range(resample_discrete_amount):
        sum_a = sum_b = sum_c = 0
        for j in range(resample_parameter):
            sum_a = sum_a + signal[i * resample_parameter + j, 0]
            sum_b = sum_b + signal[i * resample_parameter + j, 1]
            sum_c = sum_c + signal[i * resample_parameter + j, 2]
        value_a = sum_a // resample_parameter
        value_b = sum_b // resample_parameter
        value_c = sum_c // resample_parameter
        resample_signal[i,:] = np.array([value_a, value_b, value_c])
    return resample_signal
