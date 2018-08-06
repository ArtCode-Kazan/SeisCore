import numpy as np

"""
Модуль для расчета энергии по спектру

"""


def energy_calc(spectrum_data, f_min, f_max):
    """
    Функция для вычисления значения энергии по спектру
    :param spectrum_data: данные спектра (двухмерный массив с частотой (
    первая колонка) и амплитудой (вторая колонка)))
    :param f_min: минимальная частота для расчета энергии
    :param f_max: максимальная частота для расчета энергии
    :return: значение энергии

    """
    # определение участка спектра для интегрирования
    if f_min is None:
        f_min = min(spectrum_data[:, 0])
    if f_max is None:
        f_max = max(spectrum_data[:, 0])
    selected_spectrum = spectrum_data[(spectrum_data[:, 0] >= f_min) &
                                      (spectrum_data[:, 0] <= f_max)]

    # интегрирование выборки спектра для вычисления энергии
    result = np.trapz(x=selected_spectrum[:, 0],
                      y=selected_spectrum[:, 1])
    return result
