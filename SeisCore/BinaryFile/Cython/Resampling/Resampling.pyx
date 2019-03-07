import numpy as np
cimport numpy as np
cimport cython


np.import_array()

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
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
        int i, j, k
        # Вычисление сумм для нахождения среднего
        int sum_a, sum_b, sum_c
        # Вычисленные значения после ресемплирования
        int value_a, value_b, value_c
        # Создание выходного массива
        np.ndarray[np.int_t, ndim = 2] resample_signal

    # проверка кратности длины сигнала и параметра ресемплирования
    discrete_amount = signal.shape[0]

    # расчет длины ресемплированного сигнала
    resample_discrete_amount = discrete_amount // resample_parameter

    resample_signal = np.empty(shape=(resample_discrete_amount,3),
                               dtype=np.int)

    # операция ресемплирования
    for i in range(resample_discrete_amount):
        sum_a = sum_b = sum_c = 0
        for j in range(resample_parameter):
            k = i * resample_parameter + j
            sum_a = sum_a + signal[k, 0]
            sum_b = sum_b + signal[k, 1]
            sum_c = sum_c + signal[k, 2]
        value_a = sum_a // resample_parameter
        value_b = sum_b // resample_parameter
        value_c = sum_c // resample_parameter
        resample_signal[i,:] = np.array([value_a, value_b, value_c])
    return resample_signal
