# coding=utf-8
"""
Данный модуль содержит функции для первичной обработки данных ГРП
"""

import numpy as np


def reproject_coords(points_coords, x_central=0, y_central=0):
    """
    Функция перевода координат в условную СК
    :param points_coords: двухмерный массив numpy с координатами датчиков
    :param x_central: координата x центральной точки
    :param y_central: координата y центральной точки
    :return: список экземпляров класса GRPPoint c пересчитанными координатами
    """
    # пересчет координат
    result = np.empty(shape=(points_coords.shape[0], 2), dtype=float)
    for i in range(points_coords.shape[0]):
        result[i, 0] = points_coords[i, 0] - x_central
        result[i, 1] = points_coords[i, 1] - y_central
    return result


def nodes(radius, count_nodes):
    """
    Функция генерации условных координат узлов по окружности для расчета
    максимального и
    минимального времи задержки
    :param radius: радиус окружности
    :param count_nodes: количество узлов на окружности
    :return: numpy-массив с координатами узлов
    """
    result = np.empty(shape=(count_nodes, 2), dtype=float)
    alpha_deg = np.linspace(0, 360, count_nodes)
    alpha_rad = np.deg2rad(alpha_deg)

    x = radius * np.cos(alpha_rad)
    y = radius * np.sin(alpha_rad)
    result[:, 0] = x
    result[:, 1] = y
    return result


def calc_time(x1, y1, z1, x2, y2, z2, velocity):
    """
    Функция для расчета времени прихода сигнала
    :param x1: x-координата точки 1 в метрах
    :param y1: y-координата точки 1 в метрах
    :param z1: z-координата точки 1 в метрах
    :param x2: x-координата точки 2 в метрах
    :param y2: y-координата точки 2 в метрах
    :param z2: z-координата точки 2 в метрах
    :param velocity: скорость среды в м/с
    :return: время в секундах
    """
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
    result = distance / velocity
    return result


def calc_angle(x_sensor1, y_sensor1, z_sensor1, x, y, z, x_sensor2, y_sensor2,
               z_sensor2):
    """
    Функция вычисления угла между датчиками и точкой в пространстве
    :param x_sensor1: координата x датчика 1
    :param y_sensor1: координата y датчика 1
    :param z_sensor1: координата z датчика 1
    :param x: координата x точки пространства
    :param y: координата y точки пространства
    :param z: координата z точки пространства
    :param x_sensor2: координата x датчика 2
    :param y_sensor2: координата y датчика 2
    :param z_sensor2: координата z датчика 2
    :return: угол между лучами от от точки пространства к двум датчикам в
    градусах
    """
    l_ab = ((x_sensor1 - x) ** 2 + (y_sensor1 - y) ** 2 + (
            z_sensor1 - z) ** 2) ** 0.5
    l_bc = ((x_sensor1 - x_sensor2) ** 2 + (y_sensor1 - y_sensor2) ** 2 +
            (z_sensor1 - z_sensor2) ** 2) ** 0.5
    l_ac = ((x_sensor2 - x) ** 2 + (y_sensor2 - y) ** 2 + (
            z_sensor2 - z) ** 2) ** 0.5
    a = (l_bc ** 2 - l_ab ** 2 - l_ac ** 2) / (-2 * l_ab * l_ac)
    alpha_rad = np.arccos(a)
    alpha_deg = np.rad2deg(alpha_rad)
    return alpha_deg


def calc_time_delay(points_numbers, points_coords, radius, frequency, velocity,
                    max_depth):
    """
    Функция для расчета максимального и минимального времени задержки между
    парами датчиков в количестве отсчетов (НЕ В СЕКУНДАХ, А В ОТСЧЕТАХ!)
    :param points_numbers: номера точек
    :param points_coords: перепроицированные координаты точек
    :param radius: радиус окружности для анализа событий метры
    :param frequency: частота дискретизации Гц
    :param velocity: скорость в среде в м/с
    :param max_depth: максимальная глубина анализа событий, метры
    :return: numpy массив с колонками: датчик 1, датчик 2 (реальный номер),
    минимальная задержка в отсчетах, максимальная задержка в отсчетах
    """
    # выходной массив
    result = np.empty(shape=0, dtype=np.int)
    # генерация координат узлов
    nodes_data = nodes(radius=radius, count_nodes=1000)
    # i и j используются только для того, чтобы избежать попадания в выходной
    # список пар датчиков (1,1), (2,2), (1, 2) и (2,1). Добавится
    # только один из них - (1, 2)
    i = 0
    for x_a, y_a in points_coords:
        i += 1
        j = 0
        for x_b, y_b in points_coords:
            j += 1
            if i < j:
                # поиск максимального и минимального времени задержки между
                # двумя датчиками от точек, находящихся на глубине
                # max_depth и в узлах квадрата и точками датчиков
                min_delta_moments = 0
                max_delta_moments = 0
                for x_node, y_node in nodes_data:
                    time_a = calc_time(x1=x_a,
                                       y1=y_a,
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
                    time_b = calc_time(x1=x_b,
                                       y1=y_b,
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
                    delta_moments = int(round(frequency * (time_b - time_a)))
                    if 0 <= delta_moments < min_delta_moments:
                        min_delta_moments = delta_moments
                    if delta_moments > max_delta_moments:
                        max_delta_moments = delta_moments
                result = np.append(result, [points_numbers[i - 1],
                                            points_numbers[j - 1],
                                            min_delta_moments,
                                            max_delta_moments])
    # изменение размера массива, чтобы данные оказались по колонкам
    column_count = 4
    rows_count = result.shape[0] // column_count
    result = np.reshape(result, newshape=(rows_count, column_count))
    return result


def calc_max_angles(points_numbers, points_coords, radius, max_depth):
    """
    Функция для расчета максимального угла между парами датчиков в градусах
    :param points_numbers: номера точек
    :param points_coords: массив с перепроицированными координатами точек
    :param radius: радиус окружности для анализа событий метры
    :param frequency: частота дискретизации Гц
    :param velocity: скорость в среде в м/с
    :param max_depth: максимальная глубина анализа событий, метры
    :return: numpy-массив с колонками датчик 1, датчик 2 (реальный номер),
    максимальный угол в градусах
    """
    # выходной массив
    result = np.empty(shape=0, dtype=np.int)
    # генерация координат узлов
    nodes_data = nodes(radius=radius, count_nodes=1000)
    # i и j используются только для того, чтобы избежать попадания в выходной
    # список пар датчиков (1,1), (2,2), (1, 2) и (2,1). Добавится только
    # один из них - (1, 2)
    i = 0
    for x_a, y_a in points_coords:
        i += 1
        j = 0
        for x_b, y_b in points_coords:
            j += 1
            if i < j:
                max_angle = -9999999
                for x_node, y_node in nodes_data:
                    alpha = calc_angle(x_sensor1=x_a,
                                       y_sensor1=y_a,
                                       z_sensor1=0,
                                       x=x_node,
                                       y=y_node,
                                       z=max_depth,
                                       x_sensor2=x_b,
                                       y_sensor2=y_b,
                                       z_sensor2=0)
                    if alpha > max_angle:
                        max_angle = alpha
                result = np.append(result, [points_numbers[i - 1],
                                            points_numbers[j - 1],
                                            max_angle])
    # изменение размера массива, чтобы данные оказались по колонкам
    column_count = 3
    rows_count = result.shape[0] // column_count
    result = np.reshape(result, newshape=(rows_count, column_count))
    return result


def pairs_points_filtration(points_numbers, points_coords, radius, frequency,
                            velocity, max_depth, max_moments_delay, max_angle):
    """
    Функция для фильтрации пар датчиков в зависимости от максимально
    допустимой временной задержки (в отсчетах) и максимально допустимого угла
    :param points_numbers: номера точек
    :param points_coords: перепроицированные координаты точек в м
    :param radius: радиус окружности для генерации узлов в м
    :param frequency: частота дискретизации в Гц
    :param velocity: скорость в среде в м/с
    :param max_depth: максимальная глубина в м
    :param max_moments_delay: максимальная задержка в отсчетах
    :param max_angle: максимальный угол в градусах
    :return:
    """
    # расчет пределов задержек в моментах
    moments_delay = calc_time_delay(points_numbers=points_numbers,
                                    points_coords=points_coords,
                                    radius=radius,
                                    frequency=frequency,
                                    velocity=velocity,
                                    max_depth=max_depth)

    # расчет максимальных углов в градусах
    angles = calc_max_angles(points_numbers=points_numbers,
                             points_coords=points_coords,
                             radius=radius,
                             max_depth=max_depth)

    # фильтрация пределов задержек по порогу максимальной задержки
    filtration_order_1 = np.empty(shape=0, dtype=np.int)
    for point_a_number, point_b_number, min_delay, max_delay in moments_delay:
        moment_range = max_delay - min_delay
        if moment_range <= max_moments_delay:
            filtration_order_1 = np.append(filtration_order_1, [point_a_number,
                                                                point_b_number])
    # изменение формы массива, чтобы пары были в строках
    column_count = 2
    rows_count = filtration_order_1.shape[0] // column_count
    filtration_order_1 = np.reshape(filtration_order_1, newshape=(rows_count,
                                                                  column_count))

    # фильтрация списка углов - второй порядок фильтрации
    filtration_order_2 = np.empty(shape=0, dtype=np.int)
    for point_a_number, point_b_number, alpha in angles:
        if alpha <= max_angle:
            for point_a, point_b in filtration_order_1:
                if point_a == point_a_number and point_b == point_b_number:
                    filtration_order_2 = np.append(filtration_order_2,
                                                   [point_a_number,
                                                    point_b_number])
                    break
    # изменение формы массива, чтобы пары были в строках
    column_count = 2
    rows_count = filtration_order_2.shape[0] // column_count
    filtration_order_2 = np.reshape(filtration_order_2, newshape=(rows_count,
                                                                  column_count))
    return filtration_order_2
