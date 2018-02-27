import numpy as np
from SeisCore.HydroFracCore.CalcFunctions.MomentsSelection import nodes,\
    calc_time,calc_angle


def calc_time_delay(points_coords, radius, frequency, velocity, max_depth):
    """
    Функция для расчета максимального и минимального времени задержки между
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
    nodes_data = nodes(radius=radius, count_nodes=1000)
    # i и j используются только для того, чтобы избежать попадания в выходной
    # список пар датчиков (1, 2) и (2,1). Добавится только один из них - (1, 2)
    i = 0
    for point_a in points_coords:
        i += 1
        j = 0
        for point_b in points_coords:
            j += 1
            if i < j:
                # поиск максимального и минимального времени задержки между
                # двумя датчиками от точек, находящихся на глубине
                # max_depth и в узлах квадрата и точками датчиков
                min_delta_moments = 99999999
                max_delta_moments = -9999999
                for x_node, y_node in nodes_data:
                    time_a = calc_time(x1=point_a[1],
                                       y1=point_a[2],
                                       z1=0,
                                       x2=x_node,
                                       y2=y_node,
                                       z2=max_depth,
                                       velocity=velocity)
                    time_b = calc_time(x1=point_b[1],
                                       y1=point_b[2],
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
                    [(point_a[0], point_b[0]),
                     (min_delta_moments, max_delta_moments)])
    return result


def calc_max_angles(points_coords, radius, max_depth):
    """
    Функция для расчета максимального угла между парами датчиков в градусах
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
    nodes_data = nodes(radius=radius, count_nodes=1000)
    # i и j используются только для того, чтобы избежать попадания в выходной
    # список пар датчиков (1, 2) и (2,1). Добавится только один из них - (1, 2)
    i = 0
    for point_a in points_coords:
        i += 1
        j = 0
        for point_b in points_coords:
            j += 1
            if i < j:
                max_angle = -9999999
                for x_node, y_node in nodes_data:
                    alpha = calc_angle(x_sensor1=point_a[1],
                                       y_sensor1=point_a[2],
                                       z_sensor1=0,
                                       x=x_node,
                                       y=y_node,
                                       z=max_depth,
                                       x_sensor2=point_b[1],
                                       y_sensor2=point_b[2],
                                       z_sensor2=0)
                    if alpha > max_angle:
                        max_angle = alpha
                result.append(
                    [(point_a[0], point_b[0]), max_angle])
    return result


coords_file=r'D:\AppsBuilding\TestingData\where.txt'

x_central=417339
y_central=6229250
max_depth=1991
radius=200
frequency=1000
velocity=1991/0.423


data=np.loadtxt(fname=coords_file)
data[:,1]=data[:,1]-x_central
data[:,2]=data[:,2]-y_central


moments_delay=calc_time_delay(data, radius, frequency, velocity,
                              max_depth)

alpha=calc_max_angles(data,radius,max_depth)


max_moments_delay=40
max_angle=30
# фильтрация списка пределов задержек
filtration_order_1 = list()
for points_pair, moment_delay_limit in moments_delay:
    moment_range = moment_delay_limit[1] - moment_delay_limit[0]
    if moment_range <= max_moments_delay:
        filtration_order_1.append(points_pair)

# фильтрация списка углов - второй порядок фильтрации
filtration_order_2=list()
for points_pair,alpha in alpha:
    if alpha<=max_angle:
        if points_pair in filtration_order_1:
            filtration_order_2.append(points_pair)

for el in filtration_order_2:
    print(el)

