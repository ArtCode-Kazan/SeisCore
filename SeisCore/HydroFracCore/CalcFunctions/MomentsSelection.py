"""
Данный модуль содержит функции для первичной обработки данных ГРП
"""

import numpy as np


def reproject_coords(points):
    """
    Функция перевода координат в условную СК
    :param points: список экземпляров класса GRPPoint (SeisPars)
    :return: список экземпляров класса GRPPoint c пересчитанными координатами
    """
    # поиск центральной точки
    for point in points:
        if point.type == 'Central':
            central_point = point
            break

    # пересчет координат
    for point in points:
        point.x_reproject = point.x_coord - central_point.x_coord
        point.y_reproject = point.y_coord - central_point.y_coord
    return points


def nodes(radius,count_nodes):
    """
    Функция генерации условных координат узлов по окружности для расчета
    максимального и
    минимального времи задержки
    :param radius: радиус окружности
    :param count_nodes: количесвто узлов на окружности
    :return: numpy-массив с координатами узлов
    """
    result = np.empty(shape=(count_nodes,2), dtype=float)
    alpha_deg=np.linspace(0,360,count_nodes)
    alpha_rad=np.deg2rad(alpha_deg)

    x = radius * np.cos(alpha_rad)
    y = radius * np.sin(alpha_rad)
    result[:, 0]=x
    result[:, 1]=y
    return result


# def nodes(extent):
#     """
#     Функция генерации условных координат узлов для расчета максимального и
#     минимального времи задержки
#     :param extent: размер стороны квадрата в метрах
#     :return: список с кортежами координат xy каждого узла в условной СК
#     """
#     result = list()
#     result.append((-extent / 2, extent / 2))
#     result.append((0, extent / 2))
#     result.append((extent / 2, extent / 2))
#     result.append((extent / 2, 0))
#     result.append((extent / 2, -extent / 2))
#     result.append((0, -extent / 2))
#     result.append((-extent / 2, -extent / 2))
#     result.append((-extent / 2, 0))
#     return result


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


def calc_time_delay(points, radius, frequency, velocity, max_depth):
    """
    Функция для расчета максимального и минимального времи задержки между
    парами датчиков в количестве отсчетов (НЕ В СЕКУНДАХ, А В ОТСЧЕТАХ!)
    :param points: список экземпляров класса GRPPoint (SeisPars)
    :param radius: радиус окружности для анализа событий метры
    :param frequency: частота дискретизации Гц
    :param velocity: скорость в среде в м/с
    :param max_depth: максимальная глубина анализа событий, метры
    :return: список типа [[[датчик 1, датчик 2 (реальный номер)],
    [минимальная задержка в отсчетах, максимальная задержка в отсчетах]], ... ]
    """
    # выходной список
    result = list()
    # генерация координат узлов
    nodes_data = nodes(radius=radius,count_nodes=1000)
    # i и j используются только для того, чтобы избежать попадания в выходной
    # список пар датчиков (1, 2) и (2,1). Добавится только один из них - (1, 2)
    i = 0
    for point_a in points:
        i += 1
        j = 0
        for point_b in points:
            j += 1
            if i < j:
                # поиск максимального и минимального времени задержки между
                # двумя датчиками от точек, находящихся на глубине
                # max_depth и в узлах квадрата и точками датчиков
                min_delta_moments = 99999999
                max_delta_moments = -9999999
                for x_node, y_node in nodes_data:
                    time_a = calc_time(x1=point_a.x_reproject,
                                       y1=point_a.y_reproject,
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
                    time_b = calc_time(x1=point_b.x_reproject,
                                       y1=point_b.y_reproject,
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
                    delta_moments = int(round(frequency * (time_b - time_a)))
                    if delta_moments < min_delta_moments:
                        min_delta_moments = delta_moments
                    if delta_moments > max_delta_moments:
                        max_delta_moments = delta_moments
                result.append(
                    [(point_a.number, point_b.number),
                     (min_delta_moments, max_delta_moments)])
    return result


def calc_correlation_array(signal1, signal2, window_size,
                           d_step_min, d_step_max):
    """
    Функция для расчета коэффициентов корреляции двух кусков сигналов
    :param signal1: массив сигнала 1 (одномерный, numpy)
    :param signal2: массив сигнала 2 (одномерный, numpy)
    :param window_size: размер окна расчета коэф-та корреляции (в отсчетах)
    :param d_step_min: минимальный сдвиг окна (в отсчетах)
    :param d_step_max: максимальный сдвиг окна (в отсчетах)
    :return: возвращает numpy массив вида:
    [номер левого отсчета куска первого сигнала,
    номер левого отсчета куска второго сигнала,
    значение корреляции],...
    """
    # выходной массив
    result = np.empty((0, 0), dtype=np.float32)
    # количество перестановок на первом сигнале
    up_windows_count = signal1.shape[0] - 1

    # пооконный расчет
    for i in range(up_windows_count):
        # получение выборки первого сигнала
        left_edge_signal1 = i
        right_edge_signal1 = i + window_size
        window1 = signal1[left_edge_signal1:right_edge_signal1]
        # передвижка окон по второму сигналу
        for j in range(d_step_min, d_step_max + 1, 1):
            # получение выборки второго сигнала
            left_edge_signal2 = left_edge_signal1 + j
            right_edge_signal2 = left_edge_signal2 + window_size
            # пропуск работы цикла, если границы выборки второго сигнала
            # выходят за пределы
            if left_edge_signal2 < 0 or right_edge_signal2 > signal1.shape[0]:
                continue

            window2 = signal2[left_edge_signal2:right_edge_signal2]
            # расчет коэф-та корреляции (только для окон, размеры
            # которых точно совпали)
            if window1.shape[0] == window2.shape[0]:
                correlation_coeff = np.corrcoef(window1, window2)[0, 1]
                # создание временного кортежа для вставки в выходной массив
                adding_part = (left_edge_signal1, left_edge_signal2,
                               correlation_coeff)
                # вставка временного кортежа
                result = np.append(result, adding_part)
    # изменение формы массива. т.к при вставке элементов он одномерный,
    # нужен двухмерный с тремя колонками:
    # 1 - номер левого отсчета куска первого сигнала
    # 2 - номер левого отсчета куска второго сигнала
    # 3 - значение корреляции
    result_count = result.shape[0] // 3
    result = np.reshape(result, (result_count, 3))
    return result


def correlation_filtration(correlation_data, min_correlation, moment_interval):
    """
    Функция для фильтрации значений корреляций исходя из минимального
    порогового значения и минимальной разницы времени между событиями в
    отсчетах
    :param correlation_data: массив numpy из функции calc_correlation_array
    (см. выше)
    :param min_correlation: минимальное значение корреляции
    :param moment_interval: минимальная разница времени в отсчетах
    :return: возвращает такой же массив как и функция
    calc_correlation_array, но уже отфильтрованный
    """
    # сортировка входного массива по убыванию
    correlation_sort = correlation_data[correlation_data[:, 2].argsort()[::-1]]

    # выборка из отсортированного массива тех элементов, где корреляция
    # больше минимального заданного порога
    selection_correlation = correlation_sort[(correlation_sort[:,
                                              2] >= min_correlation)]

    # создание выходного массива
    result = np.empty((0, 0), dtype=np.float32)

    # вставка первого элемента в выходной массив - это первый элемент
    # отсортированного массива
    result = np.append(result, selection_correlation[0])
    # изменение формы массива. т.к при вставке элементов он одномерный,
    # нужет двухмерный с тремя колонками:
    # 1 - номер левого отсчета куска первого сигнала
    # 2 - номер левого отсчета куска второго сигнала
    # 3 - значение корреляции
    result_count = result.shape[0] // 3
    result = np.reshape(result, (result_count, 3))

    # теперь элементы из массива selection_correlation сравниваются по
    # времени в отсчтетах по первому сигналу с элементами массива result.
    # Если время задержки окажется больше минимального, то элемент из
    # selection_correlation добавляется в массив result
    for correlation in selection_correlation:
        # получение номера левого отсчета сигнала из выборки
        moment1 = correlation[0]
        is_correct = True
        for res in result:
            # получение номера левого отсчета сигнала из результативной выборки
            moment2 = res[0]
            if abs(moment2 - moment1) < moment_interval:
                is_correct = is_correct and False
            else:
                is_correct = is_correct and True

        if is_correct is True:
            # добавление в результативную выборку, если условие соблюдено,
            # выход из вложенного цикла и переход к следующему элементу
            result = np.append(result, correlation)
            result_count = result.shape[0] // 3
            result = np.reshape(result, (result_count, 3))

    return result
