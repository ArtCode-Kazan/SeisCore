from lbfgs import fmin_lbfgs
import warnings


def target_function_coordinates(params, grad, *args):
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

    # коорднаты, которые требуется найти
    x, y, z = params
    grad[0]=0
    grad[1]=0
    grad[2]=0
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

        grad[0]+=grad_x(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[1]+=grad_y(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
        grad[2]+=grad_z(x,y,z,x_a,y_a,x_b,y_b,velocity_a,velocity_b,
                        correlation,frequency,delta_moments)
    return result


def target_function_velocities(params, grad, *args):
    """
        Целевая функция минимизации для поиска скоростей
        :param params: неизвестные координаты события - x, y, z, v1,v2,v3,...,vn
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


def minimization_coordinates(coeffs, start_coords, frequency):
    """
    Функция минимизации для поиска координат события
    :param data: массив для целевой функции
    :param start_coords: начальные координаты поиска событий
    :param frequency: частота дискретизации
    :return: x, y, z события, значение функции минимизации
    """
    warnings.filterwarnings("ignore")
    x0, y0, z0 = start_coords
    x, y, z = fmin_lbfgs(f=target_function_coordinates,
                         x0=(x0, y0, z0),
                         args=[coeffs, frequency])
    function_value = target_function_coordinates((x,y,z), [0, 0, 0],
                                                  coeffs, frequency)
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

    result = fmin_lbfgs(f=target_function_velocities,
                        x0=x0,
                        args=[points_list, coeffs, frequency])

    velocities = result[3:]
    return velocities
