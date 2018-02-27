import numpy as np

"""
Модуль для расчета энергии по спектру

"""

def energy_calc(frequencies, amplitudes, f_min, f_max):
    """
    Функция для вычисления значения энергии по спектру
    :param frequencies: одномерный массив numpy частот
    :param amplitudes: одномерный массив numpy амплитуд
    :param f_min: минимальная частота для расчета энергии
    :param f_max: максимальная частота для расчета энергии
    :return: значение энергии

    """
    # определение минимального индекса для выборки участка спектра для
    # интегрирования
    if f_min is not None:
        indexes = np.where(frequencies >= f_min)
        min_index = np.min(indexes)
    else:
        min_index = 0

    # определение максимального индекса для выборки участка спектра для
    # интегрирования
    if f_max is not None:
        indexes = np.where(frequencies <= f_max)
        max_index = np.max(indexes)
    else:
        max_index = frequencies.shape[0]

    # интегрирование выборки спектра для вычисления энергии
    result = np.trapz(y=amplitudes[min_index: max_index],
                      x=frequencies[min_index: max_index])
    return result
