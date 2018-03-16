import numpy as np

from SeisCore.GeneralPlottingFunctions.histogram import histogram


def histogram_moments_delay(time_delay_data, title_text=None):
    """
    Функция отображения гистограммы по размахам временных задержек в моментах
    :param time_delay_data: занчения, полученные из функции calc_time_delay
    (ГРП)
    :return: None
    """
    moments_delay_range=np.empty(shape=0, dtype=int)
    for point_a_number, point_b_number, min_delay, max_delay in time_delay_data:
        moment_range=max_delay-min_delay
        moments_delay_range=np.append(moments_delay_range,[moment_range])
    histogram(data=moments_delay_range,
              bin_size=5,
              histo_label=title_text)


def histogram_angles(max_angles_data, title_text=None):
    """
    Функция отображения гистограммы по максимальным углам между датчиками
    :param time_delay_data: значения, полученные из функции calc_max_angles
    (ГРП)
    :return: None
    """
    angles_data=np.empty(shape=0, dtype=int)
    for point_a_number, point_b_number, alpha in max_angles_data:
        angles_data=np.append(angles_data,[alpha])
    histogram(data=angles_data,
              bin_size=1,
              histo_label=title_text)
