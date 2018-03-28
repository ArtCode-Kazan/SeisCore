from scipy.optimize import minimize
import numpy as np


def target_function_coordinates(params, args):
    """
    Целевая функция минимизации для поиска координат события
    :param params: неизвестные координаты события - x, y, z
    :param args: известные параметры функции массив и частота дискретизации
    :return:
    """
    # коорднаты, которые требуется найти
    x, y, z = params
    # параметры-постоянные для построения функции (массив и частота)
    coeffs, frequency = args
    # сама функция
    result = 0
    # обход по всем константам (слагаемым)
    for current_data in coeffs:
        # координаты первой точки
        x_a = current_data[0]
        y_a = current_data[1]
        # скорость первой точки
        velocity_a = current_data[2]
        # координаты второй точки
        x_b = current_data[3]
        y_b = current_data[4]
        # скорость втоой точки
        velocity_b = current_data[5]
        # задержка между парой
        delta_moments = current_data[6]
        # корреляция
        correlation = current_data[7]

        t_1 = ((x-x_a)**2+(y-y_a)**2+z**2)**0.5/velocity_a
        t_2 = ((x-x_b)**2+(y-y_b)**2+z**2)**0.5/velocity_b

        result += (((t_2-t_1)*frequency-delta_moments)*correlation)**2
    return result


def minimization_coordinates(coeffs, start_coords, frequency):
    """
    Функция минимизации для поиска координат события
    :param data: массив для целевой функции
    :param start_coords: начальные координаты поиска событий
    :param frequency: частота дискретизации
    :return: x, y, z события

    """
    x0, y0, z0 = start_coords
    result = minimize(fun=target_function_coordinates,
                      x0=np.array([x0, y0, z0]),
                      args=[coeffs, frequency])
    x, y, z = result.x
    z = abs(z)
    return x, y, z
