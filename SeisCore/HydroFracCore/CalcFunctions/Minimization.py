from scipy.optimize import minimize


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
        # скорость второй точки
        velocity_b = current_data[5]
        # задержка между парой
        delta_moments = current_data[6]
        # корреляция
        correlation = current_data[7]

        t_1 = ((x - x_a) ** 2 + (y - y_a) ** 2 + z ** 2) ** 0.5 / velocity_a
        t_2 = ((x - x_b) ** 2 + (y - y_b) ** 2 + z ** 2) ** 0.5 / velocity_b

        result += \
            (((t_2 - t_1) * frequency - delta_moments) * correlation) ** 2
    return result


def target_function_velocities(params, args):
    """
    Целевая функция минимизации для поиска скоростей
    :param params: неизвестные координаты события - x, y, z, v1,v2,v3,...,vn
    :param args: известные параметры функции массив и частота дискретизации
    :return:
    """
    # координаты, которые требуется найти
    x = params[0]
    y = params[1]
    z = params[2]
    velocities = params[3:]

    # параметры-постоянные для построения функции (массив и частота)
    points_list, coeffs, frequency = args
    # сама функция
    result = 0
    # обход по всем константам (слагаемым)
    for point_a_number, x_a, y_a, point_b_number, x_b, y_b, delta_moments, \
            correlation in coeffs:
        # скорость первой точки
        velocity_a = velocities[points_list.index(point_a_number)]
        # скорость второй точки
        velocity_b = velocities[points_list.index(point_b_number)]

        t_1 = ((x - x_a) ** 2 + (y - y_a) ** 2 + z ** 2) ** 0.5 / velocity_a
        t_2 = ((x - x_b) ** 2 + (y - y_b) ** 2 + z ** 2) ** 0.5 / velocity_b

        result += \
            (((t_2 - t_1) * frequency - delta_moments) * correlation) ** 2
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
                      x0=(x0, y0, z0),
                      args=[coeffs, frequency])
    x, y, z = result.x
    z = abs(z)
    function_value=result.fun
    return x, y, z, function_value


def minimization_velocities(points_list, coeffs, start_coords, start_velocity,
                            frequency):
    """
    Функция минимизации для поиска скоростей
    :param data: массив для целевой функции
    :param start_coords: начальные координаты поиска событий
    :param frequency: частота дискретизации
    :return: x, y, z события

    """
    x0, y0, z0 = start_coords
    points_count = len(points_list)
    v0 = [start_velocity] * points_count

    x0 = [x0, y0, z0] + v0

    result = minimize(fun=target_function_velocities,
                      x0=x0,
                      args=[points_list, coeffs, frequency])
    velocities = result.x[3:]
    return velocities
