import numpy as np
from scipy.optimize import minimize
from datetime import datetime

from lbfgs import fmin_lbfgs

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
    return result.x


path=r'D:\TEMP\opt_test\data.dat'

moment_data = np.loadtxt(path,dtype=np.float)

minimization_array=np.empty(shape=(moment_data.shape[0], 8),dtype=np.float)
minimization_array[:, 0] = moment_data[:, 0]
minimization_array[:, 1] = moment_data[:, 3]
minimization_array[:, 2] = moment_data[:, 4]
minimization_array[:, 3] = moment_data[:, 6]
minimization_array[:, 4] = moment_data[:, 7]
minimization_array[:, 5] = moment_data[:, 8]
minimization_array[:, 6] = moment_data[:, 10]
minimization_array[:, 7] = moment_data[:, 11]
max_depth=3250
frequency=1000
velocity=4217
point_numbers=[1.,6.,7.,11.,12.,13.,15.,16.,17.,18.,19.,25.]

t1=datetime.now()
res = \
    minimization_velocities(points_list=point_numbers,
                            coeffs=minimization_array,
                            start_coords=[0, 0, max_depth],
                            start_velocity=velocity,
                            frequency=frequency)
t2=datetime.now()
dt=(t2-t1).total_seconds()
print(dt, res)
