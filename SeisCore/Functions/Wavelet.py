from pywt import Wavelet, dwt_max_level, wavedec, waverec
import numpy as np

"""
Модуль для детрендирования сигнала с помощью вейвлет-преобразования
"""


def dwt(signal, level):
    """
    функция для прямого вейвлет-преобразования с типом вейвлета Добеши-10
    :param signal: массив numpy входного сигнала
    :param level: уровень, до которого необходимо выполнить разложение
    :return: список вида: [cA_n, cD_n, cD_n-1, ..., cD2, cD1]
    (см руководство http://pywavelets.readthedocs.io/en/latest/ref/
                    dwt-discrete-wavelet-transform.html)
    """
    # Определение максимального числа уровней, на которые можно выполнить
    # разложение
    wavelet_type = Wavelet('db10')
    max_levels_count = dwt_max_level(data_len=signal.shape[0],
                                     filter_len=wavelet_type.dec_len)
    # выполнение разложения
    if level <= max_levels_count:
        result = wavedec(signal, 'db10', level=max_levels_count)
    else:
        result = None
    return result


def idwt(coeffs):
    """
    Функция обратного вейвлет-преобразования с типом вейвлета Добеши-10
    :param coeffs: список коэф-тов вида: [cA_n, cD_n, cD_n-1, ..., cD2, cD1]
    (см руководство http://pywavelets.readthedocs.io/en/latest/ref/
                    dwt-discrete-wavelet-transform.html)
    :return: массив numpy восстановленного сигнала
    """
    signal = waverec(coeffs, 'db10')
    signal = np.asarray(signal)
    return signal


def level_num(frequency, edge_frequency):
    """
    Функция для определения уровня разложения при вейвлет-преобразовании
    в зависимости от частоты дискретизации сигнала и пороговой частоты
    С каждым уровнем разложения частота уменьшается в 2 раза от предыдущей.
    :param frequency: частота дискретизации сигнала
    :param edge_frequency: пороговая частота для преобразлования
    :return: номер уровня разложения (нумерация идет с 1)
    """
    left_lim = frequency
    i = 0
    while True:
        right_lim = left_lim
        left_lim = right_lim / 2
        i += 1
        if left_lim <= edge_frequency <= right_lim:
            if (edge_frequency - left_lim) <= (right_lim - edge_frequency):
                i += 1
            else:
                i -= 1
            break
    return i


def detrend(signal, frequency, edge_frequency):
    """
    Функция детрендирования сигнала. Смысл заключается в том, что сначала
    делается прямое вейвлет-преобразование до необходимого уровня разложения.
    затем выходной массив коэф-тов An зануляется.
    :param signal: массив numpy входного сигнала
    :param frequency: частота дискретизации сигнала
    :param edge_frequency: пороговая частота
    :return: массив numpy выходного детрендированного сигнала
    """
    # получение необходимо уровня разложения
    need_level = level_num(frequency=frequency, edge_frequency=edge_frequency)
    # выполение разложения
    wavelet_data = dwt(signal=signal, level=need_level)
    # если разложение выполнено удачно, произодится детрендирование
    if wavelet_data is not None:
        # массив коэф-тов An заполняется нулями
        wavelet_data[0] = np.zeros(wavelet_data[0].shape[0], dtype=np.int)
        # восстановление сигнала, но с исправленными An
        detrend_sig = waverec(wavelet_data, 'db10')
    else:
        detrend_sig = None
    if detrend_sig.shape[0]>signal.shape[0]:
        detrend_sig=detrend_sig[:signal.shape[0]]
    elif detrend_sig.shape[0]<signal.shape[0]:
        zero_count=signal.shape[0]-detrend_sig.shape[0]
        detrend_sig=np.append(detrend_sig,[0]*zero_count)
    return detrend_sig
