import numpy as np
from datetime import datetime

from lbfgs import fmin_lbfgs


def target_function_velocities(params, grad, *args):
    """
    Целевая функция минимизации для поиска координат события
    :param params: неизвестные координаты события - x, y, z
    :param args: известные параметры функции массив и частота дискретизации
    :return:
    """
    def grad_x(x, y, z, xa, ya, xb, yb, va, vb, corr, f, dt):
        return 2 * corr ** 2 * f * ((x - xb) /
                                    (vb * (z ** 2 + (y - yb) ** 2 + (
                                                x - xb) ** 2) ** 0.5) -
                                    (x - xa) / (va * (
                        z ** 2 + (y - ya) ** 2 + (x - xa) ** 2) ** 0.5)) * \
               (f * ((z ** 2 + (y - yb) ** 2 + (x - xb) ** 2) ** 0.5 / vb -
                     (z ** 2 + (y - ya) ** 2 +
                      (x - xa) ** 2) ** 0.5 / va) - dt)

    def grad_y(x, y, z, xa, ya, xb, yb, va, vb, corr, f, dt):
        return 2 * corr ** 2 * f * ((y - yb) /
                                    (vb * (z ** 2 + (y - yb) ** 2 + (
                                                x - xb) ** 2) ** 0.5) -
                                    (y - ya) / (va * (
                        z ** 2 + (y - ya) ** 2 + (x - xa) ** 2) ** 0.5)) * \
               (f * ((z ** 2 +(y - yb) ** 2 + (x - xb) ** 2) ** 0.5 / vb -
                     (z ** 2 + (y - ya) ** 2 +
                      (x - xa) ** 2) ** 0.5 / va) - dt)

    def grad_z(x, y, z, xa, ya, xb, yb, va, vb, corr, f, dt):
        return 2 * corr ** 2 * f * (z / (vb * (z ** 2 + (y - yb) ** 2 +
                            (x - xb) ** 2) ** 0.5) - z / (va * (z ** 2 +
                            (y - ya) ** 2 + (x - xa) ** 2) ** 0.5)) * \
                (f * ((z ** 2 + (y - yb) ** 2 + (x - xb) ** 2) ** 0.5 / vb -
                (z ** 2 + (y - ya) ** 2 + (x - xa) ** 2) ** 0.5 / va) - dt)

    def grad_va(x, y, z, xa, ya, xb, yb, va, vb, corr, f, dt):
        return (2 * corr ** 2 * f * (z ** 2 + (y - ya) ** 2 +
                (x - xa) ** 2) ** 0.5 * (f * ((z ** 2 + (y - yb) ** 2 +
                (x - xb) ** 2) ** 0.5 / vb - (z ** 2 + (y - ya) ** 2 +
                (x - xa) ** 2) ** 0.5 / va) - dt)) / va ** 2

    def grad_vb(x, y, z, xa, ya, xb, yb, va, vb, corr, f, dt):
        return -(2 * corr ** 2 * f * (z ** 2 + (y - yb) ** 2 +
                 (x - xb) ** 2) ** 0.5 * (f * ((z ** 2 + (y - yb) ** 2 +
                 (x - xb) ** 2) ** 0.5 / vb - (z ** 2 + (y - ya) ** 2 +
                 (x - xa) ** 2) ** 0.5 / va) - dt)) / vb ** 2

    # коорднаты, которые требуется найти
    x, y, z = params[:3]
    v=params[3:]
    grad[0]=0
    grad[1]=0
    grad[2]=0
    for i in range(len(params)-3):
        grad[3+i]=0

    # параметры-постоянные для построения функции (массив и частота)
    points_list, coeffs, frequency = args

    # сама функция
    result = 0

    for point_a_number, x_a, y_a, point_b_number, x_b, y_b, delta_moments, \
            correlation in coeffs:
        # скорость первой точки
        velocity_a = v[points_list.index(point_a_number)]
        # скорость второй точки
        velocity_b = v[points_list.index(point_b_number)]

        t_1 = ((x - x_a) ** 2 + (y - y_a) ** 2 + z ** 2) ** 0.5 / velocity_a
        t_2 = ((x - x_b) ** 2 + (y - y_b) ** 2 + z ** 2) ** 0.5 / velocity_b

        result += \
            (((t_2 - t_1) * frequency - delta_moments) * correlation) ** 2

        grad[0]+=grad_x(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[1]+=grad_y(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[2]+=grad_z(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[3+points_list.index(point_a_number)] += \
            grad_va(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[3 + points_list.index(point_b_number)] += \
            grad_vb(x, y, z, x_a, y_a, x_b, y_b,velocity_a, velocity_b,
                        correlation, frequency,delta_moments)
    return result

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


x0, y0, z0 = (0,0,3250)
points_count = len(point_numbers)
v0 = [velocity] * points_count
x0 = [x0, y0, z0] + v0

t1=datetime.now()
result = fmin_lbfgs(f=target_function_velocities,
                    x0=x0,
                    args=[point_numbers, minimization_array, frequency])
t2=datetime.now()
dt=(t2-t1).total_seconds()
print(dt,result)
# print(target_function_coordinates(result,[0,0,0],minimization_array,
#                                                   frequency))